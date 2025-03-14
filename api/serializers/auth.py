from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from api.models import Clinic, ClinicMembership

class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name']
        read_only_fields = ['id', 'full_name']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username

class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'password', 'password2', 'email', 'first_name', 'last_name']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom token serializer that includes user info and clinics"""
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add user data
        user = self.user
        data['user'] = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'full_name': f"{user.first_name} {user.last_name}".strip() or user.username,
        }
        
        # Add clinics data
        memberships = ClinicMembership.objects.filter(user=user).select_related('clinic')
        clinics = []
        
        for membership in memberships:
            clinics.append({
                'id': membership.clinic.id,
                'name': membership.clinic.name,
                'role': membership.role,
                'is_primary': membership.is_primary,
            })
        
        data['clinics'] = clinics
        
        # Add current clinic if user has a primary clinic
        primary_membership = memberships.filter(is_primary=True).first()
        if primary_membership:
            data['current_clinic'] = {
                'id': primary_membership.clinic.id,
                'name': primary_membership.clinic.name,
                'role': primary_membership.role,
            }
        elif memberships.exists():
            # If no primary clinic, use the first one
            first_membership = memberships.first()
            data['current_clinic'] = {
                'id': first_membership.clinic.id,
                'name': first_membership.clinic.name,
                'role': first_membership.role,
            }
        else:
            data['current_clinic'] = None
        
        return data

class ClinicSelectionSerializer(serializers.Serializer):
    """Serializer for selecting a clinic"""
    clinic_id = serializers.IntegerField(required=True)
    
    def validate_clinic_id(self, value):
        user = self.context['request'].user
        
        try:
            # Check if the user is a member of this clinic
            membership = ClinicMembership.objects.get(user=user, clinic_id=value)
            return value
        except ClinicMembership.DoesNotExist:
            raise serializers.ValidationError("You are not a member of this clinic.")

class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for changing password"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is not correct")
        return value 