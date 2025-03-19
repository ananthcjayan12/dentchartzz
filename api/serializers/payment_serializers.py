class PaymentSummarySerializer(serializers.Serializer):
    total_billed = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_paid = serializers.DecimalField(max_digits=10, decimal_places=2)
    balance_due = serializers.DecimalField(max_digits=10, decimal_places=2)
    last_payment_date = serializers.DateField(allow_null=True) 