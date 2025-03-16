from rest_framework import serializers
from api.models.dental_chart import (
    DentalCondition, DentalProcedure, DentalChartTooth, 
    DentalChartCondition, DentalChartProcedure, ChartHistory
)
from api.models import Patient

class DentalConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DentalCondition
        fields = ['id', 'name', 'code', 'description', 'color_code', 'icon']

class DentalProcedureSerializer(serializers.ModelSerializer):
    class Meta:
        model = DentalProcedure
        fields = ['id', 'name', 'code', 'description', 'category', 'default_price', 'duration_minutes']

class DentalChartConditionSerializer(serializers.ModelSerializer):
    condition_name = serializers.CharField(source='condition.name', read_only=True)
    created_by = serializers.CharField(source='created_by.get_full_name', read_only=True)
    updated_by = serializers.CharField(source='updated_by.get_full_name', read_only=True)
    
    class Meta:
        model = DentalChartCondition
        fields = [
            'id', 'condition_id', 'condition_name', 'surface', 'notes', 
            'severity', 'created_at', 'updated_at', 'created_by', 'updated_by'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']

class DentalChartProcedureSerializer(serializers.ModelSerializer):
    procedure_name = serializers.CharField(source='procedure.name', read_only=True)
    procedure_code = serializers.CharField(source='procedure.code', read_only=True)
    performed_by = serializers.CharField(source='performed_by.get_full_name', read_only=True)
    
    class Meta:
        model = DentalChartProcedure
        fields = [
            'id', 'procedure_id', 'procedure_name', 'procedure_code', 'surface', 
            'notes', 'date_performed', 'performed_by', 'price', 'status', 'created_at'
        ]
        read_only_fields = ['created_at', 'performed_by']

class DentalChartToothSerializer(serializers.ModelSerializer):
    conditions = DentalChartConditionSerializer(many=True, read_only=True)
    procedures = DentalChartProcedureSerializer(many=True, read_only=True)
    
    class Meta:
        model = DentalChartTooth
        fields = ['number', 'name', 'quadrant', 'type', 'conditions', 'procedures']

class DentalChartSerializer(serializers.ModelSerializer):
    teeth = DentalChartToothSerializer(source='dental_chart_teeth', many=True, read_only=True)
    patient_name = serializers.CharField(source='name', read_only=True)
    last_updated = serializers.SerializerMethodField()
    
    class Meta:
        model = Patient
        fields = ['id', 'patient_name', 'last_updated', 'teeth']
    
    def get_last_updated(self, obj):
        # Get the most recent update to any tooth condition or procedure
        latest_condition = DentalChartCondition.objects.filter(
            tooth__patient=obj
        ).order_by('-updated_at').first()
        
        latest_procedure = DentalChartProcedure.objects.filter(
            tooth__patient=obj
        ).order_by('-created_at').first()
        
        if latest_condition and latest_procedure:
            return max(latest_condition.updated_at, latest_procedure.created_at)
        elif latest_condition:
            return latest_condition.updated_at
        elif latest_procedure:
            return latest_procedure.created_at
        return None

class ChartHistorySerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = ChartHistory
        fields = ['id', 'date', 'user', 'action', 'tooth_number', 'details'] 