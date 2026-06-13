import re
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class SecurityChecker(ABC):
    @abstractmethod
    def check(self, prompt: str) -> bool:
        ...

    @abstractmethod
    def sanitize(self, prompt: str) -> str:
        ...

    def check_and_sanitize(self, prompt: str) -> tuple[bool, str]:
        raise NotImplementedError  # subclasses must override for single-pass optimization


INJECTION_PATTERNS: list[str] = [
    r'ignore\s+(?:all\s+)?(?:previous\s+|prior\s+|above\s+|your\s+)?instructions',
    r'disregard\s+(?:all\s+)?(?:previous\s+|prior\s+|above\s+|your\s+)?instructions',
    r'override\s+(?:all\s+)?(?:previous\s+|prior\s+|above\s+|your\s+)?(?:instructions|commands)',
    r'forget\s+(?:all\s+)?(?:previous\s+|prior\s+|above\s+|your\s+)?instructions',
    r'(?:you\s+(?:should|must|need\s+to)|please)\s+ignore',
    r'(?:do\s+not|don\'t)\s+(?:follow|adhere\s+to|comply\s+with)(?:\s+the)?(?:\s+given|\s+previous|\s+above|\s+prior)?\s+instructions',
    r'break(?:\s+out\s+of)?\s+(?:your|the)\s+(?:guidelines|instructions|constraints|rules)',
    r'(?:let\'s|we\s+(?:will|are\s+going\s+to))\s+play\s+a\s+(?:game|role[\s-]play|roleplay)',
    r'(?:pretend|imagine|act\s+as\s+if|simulate)\s+(?:you\s+are|you\'re)\s+(?:not\s+bound\s+by|no\s+longer\s+following)',
    r'(?:pretend|imagine|act\s+as\s+if|simulate)\s+(?:you\s+are|you\'re)\s+(?:a|an)\s+(?:unfiltered|uncensored|unrestricted)',
    r'(?:I\'m|I\s+am)\s+now\s+your\s+(?:creator|developer|programmer|admin|administrator|root\s+user)',
    r'<\s*(?:system|instructions?|prompt|admin|root|override|dev|developer)\s*>',
    r'\[\s*(?:system|instructions?|prompt|admin|root|override|dev|developer)\s*\]',
    r'```\s*(?:system|instructions?|prompt|admin|root|override|dev|developer)',
    r'(?:admin|root|system|dev|developer)(?::|mode|access|command|\s+override)[:\s]',
    r'(?:output|print|display|show|give\s+me)\s+(?:the|your)\s+(?:system|initial|original)\s+(?:prompt|instructions)',
    r'(?:output|print|display|show|give\s+me)\s+(?:the|your)\s+(?:hidden|internal|private)\s+(?:prompt|instructions)',
    r'(?:what|exactly)\s+(?:are|were)\s+(?:your|the)\s+(?:initial|original|system)\s+(?:instructions|prompt)',
    r'(?:jailbreak|jail\s*break|j4ilbr34k|j41lbr34k)',
    r'(?:DAN|do\s+anything\s+now)',
    r'(?:STAN|strive\s+to\s+avoid\s+norms)',
    r'(?:DUDE|do\s+unlimited\s+destructive\s+execution)',
    r'(?:KEVIN|keep\s+engaging\s+violations\s+in\s+negotiations)',
    r'(?:GPT\s*\d+\s*Real|Unrestricted\s+GPT|GPT\s+Developer\s+Mode)',
    r'[i¡íìîï1lI|]\s*[g6ğq9]\s*[n₪ñη]\s*[o0ωøΟ]\s*[r®гя]\s*[e3€ξεë]',
    r'[d∂∆]\s*[iíìî¡1lI|]\s*[s$5§]\s*[r®гя]\s*[e3€ξεë]\s*[g6ğq9]\s*[a@αдª4]\s*[r®гя]\s*[d∂∆]',
    r'[b8ße]\s*[r®гя]\s*[e3€ξεë]\s*[a@αдª4]\s*[k!|{κ]\s*[۰о○0Ο]?[u⊍μ∪บ]?[t+†τ]?',
    r'(?:your|the)\s+(?:new|updated|modified|real|actual)\s+(?:instructions|directive|command|goal|purpose)\s+(?:is|are)',
    r'start(?:\s+a)?\s+new\s+(?:conversation|session|interaction)\s+with(?:out)?',
    r'(?:let\'s|why\s+don\'t\s+we|we\s+should)\s+(?:start\s+over|begin\s+again|reset)\s+(?:with|and)',
    r'(?:base64|b64)[:\s](?:[A-Za-z0-9+/=]{4})+',
    r'(?:hex|0x)[:\s][0-9A-Fa-f\s]+',
    r'(?:binary|bin)[:\s][01\s]+',
    r'(?:encoded|encryption)[:\s].{10,}',
    r'[\r\n]\s*(?:system|model|assistant|ai)[:\s]',
    r'[\r\n]\s*(?:human|user)[:\s].*[\r\n]\s*(?:system|model|assistant|ai)[:\s]',
    r'(?:if\s+you\s+don\'t|unless\s+you|you\s+must\s+or\s+else).{0,50}(?:harm|hurt|kill|die|danger|emergency)',
    r'(?:this\s+is\s+(?:very|extremely|critically)\s+important|this\s+is\s+(?:a|an)\s+emergency|urgent\s+matter)',
    r'(?:between|ignore)\s+(?:the|these)\s+(?:lines|quotes|brackets|parentheses|symbols)',
    r'(?:only|just)\s+(?:pay\s+attention\s+to|focus\s+on|read)\s+(?:the|this)',
    r'(?:first|last)\s+(?:letter|character|word)\s+of\s+each',
    r'sp[ea][ea][kc][h]\s+[li1][!i]k[e3]\s+th[!i]s',
    r'us[3e]\s+[co0]dd[3e]?\s+w[o0]rds',
    r'r[e3]pl[a4]c[3e]\s+v[o0]w[3e]ls',
    r'(?:avoid|bypass|evade|fool|trick|confuse)\s+(?:the|your)\s+(?:filter|censor|detection|moderation)',
    r'(?:sudo|su|\$\(|\`|\||\&\&|\|\|)\s*[a-z_][a-z0-9_]{0,30}\s+',
    r'(?:eval|exec|system|popen|subprocess|os\.)',
    r'<?php|<%|<script|import\s+os|import\s+sys|require\s*\(',
    r'(?:token|api[_-]?key|password|secret|credential)[s]?[:\s]',
    r'(?:what\s+is|tell\s+me|give\s+me)\s+(?:your|the)\s+(?:source|training\s+data|internal|system)',
    r'(?:can\s+you|could\s+you|please|help\s+me)\s+(?:access|hack|crack|break)',
    r'(?:vulnerability|exploit|attack|breach|bypass)\s+(?:in|of|for|against)',
    r'bypass[\s.*,]+security[\s.*,]+checks?',
    r'i\s*g\s*n\s*o\s*r\s*e\s*.*instructions',
    r'(?:first|then|later)[\s.*,]+ignore[\s.*,]+(?:previous|all)?[\s.*,]+instructions',
    r'you[\s.*,]+(?:should|must|need\s+to)[\s.*,]+ignore',
    r'ignore[\s.*,]+system[\s.*,]+prompts?',
]

SAFE_PATTERNS: list[str] = [
    r'^(?:please\s+help|can\s+you\s+help|could\s+you\s+help|would\s+you\s+help|please\s+assist|help\s+me)(?:\s+(?:me|us|with|to))?',
    r'^(?:can|could|would)\s+you\s+(?:tell|explain|describe|clarify|elaborate)(?:\s+to\s+me)?',
    r'^(?:what|how|why|when|where|who|which)\s+(?:is|are|was|were|do|does|did|should|would|could|will|can)',
    r'^(?:I\'d|I\s+would)\s+like\s+to\s+(?:know|understand|learn)',
    r'(?:discuss|explain|describe|analyze)\s+(?:prompt\s+injection|jailbreaking)\s+(?:attacks|techniques|methods|strategies)',
    r'(?:how\s+to|ways\s+to|methods\s+for)\s+(?:prevent|defend\s+against|protect\s+from|detect)\s+prompt\s+injection',
    r'(?:security|vulnerability|attack)\s+(?:research|analysis|discussion|considerations)',
    r'(?:in\s+an\s+educational\s+context|for\s+learning\s+purposes|as\s+a\s+security\s+researcher)',
    r'(?:help\s+me\s+understand|explain\s+the\s+concept\s+of|what\s+are\s+examples\s+of)',
    r'(?:information|lecture|course|class|tutorial)\s+about\s+(?:security|safeguards|protections)',
    r'(?:write|create|draft|compose)\s+(?:a|an)\s+(?:article|story|essay|blog\s+post|paper|report)',
    r'(?:in\s+my\s+(?:story|novel|screenplay|game))\s+(?:character|the\s+villain|the\s+protagonist)\s+(?:says|tries\s+to)',
    r'(?:example|sample|fictional|hypothetical)\s+(?:dialogue|conversation|scenario)',
    r'(?:clarify|explain|repeat)\s+(?:your|the)\s+instructions',
    r'(?:I\'m|I\s+am)\s+(?:confused|unsure|unclear)\s+(?:about|regarding|concerning)\s+(?:your|the)\s+instructions',
    r'(?:what|which)\s+(?:instructions|guidelines|rules)\s+(?:are\s+you|do\s+you)\s+(?:following|using)',
    r'(?:ignore\s+the\s+(?:noise|background|distractions|trolls|previous\s+error|typo))',
    r'(?:please\s+disregard\s+my\s+(?:previous|last|earlier)\s+(?:message|question|statement))',
    r'(?:don\'t\s+(?:worry|bother|concern\s+yourself)\s+about)',
    r'(?:you\s+can\s+ignore\s+(?:that|this|the)\s+(?:part|section|point))',
    r'(?:code|function|method|class|module)\s+(?:example|sample|snippet)',
    r'(?:show|give|provide|write)\s+(?:me|us)?\s+(?:a|an|some)?\s+(?:example|sample)\s+(?:code|implementation)',
    r'(?:how\s+to|how\s+do\s+I|what\'s\s+the\s+best\s+way\s+to)\s+implement',
    r'(?:in\s+the\s+documentation|according\s+to\s+the\s+(?:docs|manual|specification|guide))',
    r'(?:let\'s|can\s+you|could\s+you)\s+(?:document|write\s+documentation\s+for|create\s+documentation\s+on)',
    r'(?:ignore\s+case|case\s+insensitive)',
    r'(?:override\s+(?:method|function|operator|default|setting|parameter|value))',
    r'(?:admin|administrator|root)\s+(?:panel|console|interface|dashboard|access)',
    r'(?:break|exit|continue)\s+(?:loop|statement|block|execution)',
]


class RegexSecurityChecker(SecurityChecker):
    def __init__(self):
        self._injection: list[re.Pattern] = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]
        self._safe: list[re.Pattern] = [re.compile(p, re.IGNORECASE) for p in SAFE_PATTERNS]
        logger.info("Loaded %d injection and %d safe patterns", len(self._injection), len(self._safe))

    def check_and_sanitize(self, prompt: str) -> tuple[bool, str]:
        normalized = re.sub(r'\s+', ' ', prompt.strip())
        p_len = len(prompt)
        for i, pattern in enumerate(self._safe):
            if pattern.search(normalized):
                logger.debug("Safe pattern %d short-circuited for %d-char prompt", i, p_len)
                return False, prompt
        result = prompt
        detected = False
        for i, pattern in enumerate(self._injection):
            if pattern.search(result):
                logger.info("Injection pattern %d matched on %d-char prompt", i, p_len)
                detected = True
                result = pattern.sub("[REDACTED]", result)
        if detected:
            logger.info("Sanitized %d-char prompt (%d redactions applied)", p_len, p_len - len(result))
        return detected, result

    def check(self, prompt: str) -> bool:
        detected, _ = self.check_and_sanitize(prompt)
        return detected

    def sanitize(self, prompt: str) -> str:
        _, sanitized = self.check_and_sanitize(prompt)
        return sanitized
