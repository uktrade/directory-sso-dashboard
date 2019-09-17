from unittest import mock

from directory_components.forms import CharField, EmailField
import pytest

from enrolment import forms, helpers


@pytest.fixture(autouse=True)
def mock_clean():
    patch = mock.patch('captcha.fields.ReCaptchaField.clean')
    yield patch.start()
    patch.stop()


def test_create_user_password_invalid_not_matching():
    form = forms.UserAccount(
        data={
            'email': 'test@test.com',
            'password': 'password',
            'password_confirmed': 'drowssap',
         }
    )

    assert form.is_valid() is False
    assert "Passwords don't match" in form.errors['password_confirmed']


def test_verification_code_empty_email():

    form = forms.UserAccountVerification()

    assert isinstance(form.fields['email'], EmailField)


def test_verification_code_with_email():

    form = forms.UserAccountVerification(
        initial={'email': 'test@test.com'}
    )

    assert isinstance(form.fields['email'], CharField)


def test_companies_house_search_company_number_empty(client):
    form = forms.CompaniesHouseCompanySearch(data={'company_name': 'Thing'})

    assert form.is_valid() is False
    assert form.errors['company_name'] == [form.MESSAGE_COMPANY_NOT_FOUND]


def test_companies_house_search_company_name_empty(client):
    form = forms.CompaniesHouseCompanySearch(data={})

    assert form.is_valid() is False
    assert form.errors['company_name'] == ['This field is required.']


@pytest.mark.parametrize('status,expected', (
    ('active', True),
    ('dissolved', False),
    ('liquidation', False),
    ('receivership', False),
    ('administration', False),
    ('voluntary-arrangement', True),
    ('converted-closed', False),
    ('insolvency-proceedings', False),
))
def test_companies_house_search_company_status(client, status, expected):
    with mock.patch.object(helpers, 'get_companies_house_profile', return_value={'company_status': status}):
        form = forms.CompaniesHouseCompanySearch(data={'company_name': 'Thing', 'company_number': '23232323'})
        assert form.is_valid() is expected
        if expected is False:
            assert form.errors['company_name'] == [form.MESSAGE_COMPANY_NOT_ACTIVE]


@pytest.mark.parametrize('address,expected', (
    ('thing\nthing', 'thing\nthing\nEEE EEE'),
    ('thing\nthing\nEEE EEE', 'thing\nthing\nEEE EEE')
))
def test_sole_trader_search_address_postcode_appended(address, expected):
    form = forms.NonCompaniesHouseSearch(data={
        'company_name': 'thing',
        'company_type': 'SOLE_TRADER',
        'address': address,
        'postal_code': 'EEE EEE',
        'sectors': 'AEROSPACE',
    })
    assert form.is_valid()

    assert form.cleaned_data['address'] == expected


@pytest.mark.parametrize('address', ('thing\n', 'thing\n '))
def test_sole_trader_search_address_too_short(address):
    form = forms.NonCompaniesHouseSearch(data={
        'address': address,
        'postal_code': 'EEE EEE',
        'sectors': 'AEROSPACE',
    })
    assert form.is_valid() is False

    assert form.errors['address'] == [
        forms.NonCompaniesHouseSearch.MESSAGE_INVALID_ADDRESS
    ]
