from payments import FraudStatus


BRAINTREE_RISK_TO_FRAUD = {
    'Not Evaluated': FraudStatus.UNKNOWN,
    'Approve': FraudStatus.ACCEPT,
    'Decline': FraudStatus.REJECT,
    'Review': FraudStatus.REVIEW,
}
