"""
Proxy models for admin reports section
These models don't create database tables - they're just for organizing admin interface
"""

from django.db import models


class UserReport(models.Model):
    """Proxy model for User Reports in admin"""

    class Meta:
        managed = False  # Don't create database table
        verbose_name = "User Report"
        verbose_name_plural = "User Reports"
        app_label = "restaurant"  # Replace 'restaurant' with your app name


class SalesReport(models.Model):
    """Proxy model for Sales Reports in admin"""

    class Meta:
        managed = False  # Don't create database table
        verbose_name = "Sales Report"
        verbose_name_plural = "Sales Reports"
        app_label = "restaurant"  # Replace 'restaurant' with your app name
