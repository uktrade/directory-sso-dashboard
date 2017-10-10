from config import context_processors


def test_feature_flags_installed(settings):
    processors = settings.TEMPLATES[0]['OPTIONS']['context_processors']

    assert 'config.context_processors.feature_flags' in processors


def test_feature_returns_expected_features(settings):
    settings.FEATURE_MULTI_USER_ACCOUNT_ENABLED = True
    settings.FEATURE_NEW_SHARED_HEADER_ENABLED = False

    actual = context_processors.feature_flags(None)

    assert actual == {
        'features': {
            'FEATURE_MULTI_USER_ACCOUNT_ENABLED': True,
            'FEATURE_NEW_SHARED_HEADER_ENABLED': False,
        }
    }


def test_analytics(rf, settings):
    settings.GOOGLE_TAG_MANAGER_ID = '123'
    settings.GOOGLE_TAG_MANAGER_ENV = '?thing=1'
    settings.UTM_COOKIE_DOMAIN = '.thing.com'

    actual = context_processors.analytics(None)

    assert actual == {
        'analytics': {
            'GOOGLE_TAG_MANAGER_ID': '123',
            'GOOGLE_TAG_MANAGER_ENV': '?thing=1',
            'UTM_COOKIE_DOMAIN': '.thing.com',
        }
    }


def test_analytics_installed(settings):
    processors = settings.TEMPLATES[0]['OPTIONS']['context_processors']

    assert 'config.context_processors.analytics' in processors
