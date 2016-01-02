import unittest

from django.db import connection
from django.test import TestCase, TransactionTestCase
from django.utils import timezone

from .models import (
    DelegatedWithDBDefault, OnlyDelegatedFields, WithDelegatedFields,
)


class DelegatedFieldsTestCase(TestCase):

    def test_delegated(self):
        obj = WithDelegatedFields.objects.create(a="John")
        self.assertIsNone(obj.a)
        obj.a = "Lorem Ipsum"
        obj.save()
        self.assertIsNone(obj.a)

    def test_model_with_only_delegated_fields(self):
        obj = OnlyDelegatedFields.objects.create(a="John")
        self.assertIsNone(obj.a)
        obj.a = "Lorem Ipsum"
        obj.save()
        self.assertIsNotNone(obj.a)

        obj.refresh_from_db()
        self.assertIsNone(obj.a)

        obj.save(ignore_delegated_fields=['a'])
        self.assertIsNone(obj.a)

    def test_ignore_delegated_fields(self):
        obj = OnlyDelegatedFields.objects.create(a="John")
        self.assertIsNone(obj.a)
        obj.a = "Lorem Ipsum"
        obj.save(ignore_delegated_fields=['a'])
        self.assertEqual(obj.a, "Lorem Ipsum")

        obj.refresh_from_db()
        self.assertEqual(obj.a, "Lorem Ipsum")


@unittest.skipUnless(connection.vendor == 'postgresql', "PostgreSQL specific tests")
class DelegatedPostgreSQLFieldsTestCase(TransactionTestCase):

    available_apps = ['delegated_fields']

    def test_delegated_with_db_defaults(self):
        '''
        Trigger sets now to current date
        '''
        now = timezone.now()
        obj = DelegatedWithDBDefault.objects.create()
        self.assertIsNotNone(obj.now)
        self.assertTrue(obj.now >= now)

    def test_returning_values_with_trigger(self):
        '''
        Database trigger set the `num` field to 0 if num is NULL.
        If num is not null, it doubles and sets the provided value
        '''
        obj = DelegatedWithDBDefault.objects.create()
        self.assertEqual(obj.num, 0)

        obj.num = 100
        obj.save()

        self.assertEqual(obj.num, 200)

    def test_return_on_insert(self):
        '''
        num_a is always set to 1 by database
        '''
        obj = DelegatedWithDBDefault.objects.create()
        self.assertEqual(obj.num_a, 1)

        obj.num_a = 2
        obj.save()
        self.assertEqual(obj.num_a, 2)

    def test_return_on_update(self):
        '''
        num_b is always set to 1 by database
        '''
        obj = DelegatedWithDBDefault.objects.create()
        self.assertEqual(obj.num_b, None)

        obj.num_b = 2
        obj.save()
        self.assertEqual(obj.num_b, 1)
