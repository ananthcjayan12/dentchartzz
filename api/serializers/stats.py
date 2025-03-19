from rest_framework import serializers

class PatientStatsSerializer(serializers.Serializer):
    totalPatients = serializers.IntegerField()
    monthlyGrowth = serializers.FloatField()
    newPatientsThisMonth = serializers.IntegerField()
    activePatients = serializers.IntegerField()

class AppointmentStatsSerializer(serializers.Serializer):
    todayCount = serializers.IntegerField()
    dailyChange = serializers.IntegerField()
    monthlyRevenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    revenueChange = serializers.FloatField()
    completionRate = serializers.FloatField()
    upcomingCount = serializers.IntegerField()
    cancelledCount = serializers.IntegerField() 