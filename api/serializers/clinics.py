from rest_framework import serializers
from django.contrib.auth.models import User
from api.models import Clinic, ClinicMembership

class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model (simplified version for clinic membership)"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id', 'username', 'email']

class ClinicMembershipSerializer(serializers.ModelSerializer):
    """Serializer for ClinicMembership model"""
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True
    )
    
    class Meta:
        model = ClinicMembership
        fields = ['id', 'user', 'user_id', 'clinic', 'role', 'is_primary', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class ClinicSerializer(serializers.ModelSerializer):
    """Serializer for Clinic model (list view)"""
    class Meta:
        model = Clinic
        fields = ['id', 'name', 'address', 'phone', 'email', 'subscription_plan', 
                  'subscription_status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class ClinicDetailSerializer(serializers.ModelSerializer):
    """Serializer for Clinic model (detail view) with memberships"""
    memberships = ClinicMembershipSerializer(many=True, read_only=True)
    
    class Meta:
        model = Clinic
        fields = ['id', 'name', 'address', 'phone', 'email', 'subscription_plan', 
                  'subscription_status', 'settings', 'created_at', 'updated_at', 'memberships']
        read_only_fields = ['id', 'created_at', 'updated_at'] 