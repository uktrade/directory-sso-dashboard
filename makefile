clean:
	-find . -type f -name "*.pyc" -delete
	-find . -type d -name "__pycache__" -delete

test_requirements:
	pip install -r requirements_test.txt

FLAKE8 := flake8 . --exclude=.venv,node_modules --max-line-length=120
PYTEST := pytest . --ignore=node_modules -W ignore::DeprecationWarning --cov=. --cov-config=.coveragerc \
    --cov-report=html --cov-report=term --capture=no -vv -s $(pytest_args)
COLLECT_STATIC := python manage.py collectstatic --noinput
CODECOV := \
	if [ "$$CODECOV_REPO_TOKEN" != "" ]; then \
	   codecov ;\
	fi

test:
	$(COLLECT_STATIC) && $(FLAKE8) && $(PYTEST) && $(CODECOV)

DJANGO_WEBSERVER := \
	python manage.py collectstatic --noinput && \
	python manage.py runserver 0.0.0.0:$$PORT

django_webserver:
	$(DJANGO_WEBSERVER)

debug_test_last_failed:
	make debug_test pytest_args='--last-failed'

DEBUG_SET_ENV_VARS := \
	export PORT=8006; \
	export SECRET_KEY=debug; \
	export DEBUG=true ;\
	export SSO_SIGNATURE_SECRET=api_signature_debug; \
	export SSO_API_CLIENT_BASE_URL=http://sso.trade.great:8003/; \
	export SSO_PROXY_LOGIN_URL=http://sso.trade.great:8004/accounts/login/; \
	export SSO_PROXY_LOGOUT_URL=http://sso.trade.great:8004/accounts/logout/?next=http://profile.trade.great:8006; \
	export SSO_PROXY_PASSWORD_RESET_URL=http://sso.trade.great:8004/accounts/password/reset/; \
	export SSO_PROXY_SIGNUP_URL=http://sso.trade.great:8004/accounts/signup/?next=http://profile.trade.great:8006; \
	export SSO_PROXY_REDIRECT_FIELD_NAME=next; \
	export SSO_SESSION_COOKIE=debug_sso_session_cookie; \
	export SSO_PROFILE_URL=http://profile.trade.great:8006; \
	export SESSION_COOKIE_SECURE=false; \
	export UTM_COOKIE_DOMAIN=.trade.great; \
	export GOOGLE_TAG_MANAGER_ID=GTM-TC46J8K; \
	export GOOGLE_TAG_MANAGER_ENV=&gtm_auth=kH9XolShYWhOJg8TA9bW_A&gtm_preview=env-32&gtm_cookies_win=x; \
	export EXPORTING_OPPORTUNITIES_API_BASE_URL=https://opportunities.export.staging.uktrade.io; \
	export EXPORTING_OPPORTUNITIES_SEARCH_URL=https://opportunities.export.great.gov.uk/opportunities; \
	export FAB_EDIT_COMPANY_LOGO_URL=http://buyer.trade.great:8001/company-profile/edit/logo; \
	export FAB_EDIT_PROFILE_URL=http://buyer.trade.great:8001/company-profile; \
	export FAB_ADD_CASE_STUDY_URL=http://buyer.trade.great:8001/company/case-study/edit/; \
	export FAB_REGISTER_URL=http://buyer.trade.great:8001; \
	export FAB_ADD_USER_URL=http://buyer.trade.great:8001/account/add-collaborator/; \
	export FAB_REMOVE_USER_URL=http://buyer.trade.great:8001/account/remove-collaborator/; \
	export FAB_TRANSFER_ACCOUNT_URL=http://buyer.trade.great:8001/account/transfer/; \
	export SECURE_HSTS_SECONDS=0; \
	export PYTHONWARNINGS=all; \
	export PYTHONDEBUG=true; \
	export SECURE_SSL_REDIRECT=false; \
	export HEALTH_CHECK_TOKEN=debug; \
	export PRIVACY_COOKIE_DOMAIN=.trade.great; \
	export EXPORTING_OPPORTUNITIES_API_SECRET=debug; \
	export DIRECTORY_CONSTANTS_URL_GREAT_DOMESTIC=http://exred.trade.great:8007/; \
	export DIRECTORY_CONSTANTS_URL_FIND_A_BUYER=http://buyer.trade.great:8001/; \
	export DIRECTORY_CONSTANTS_URL_SELLING_ONLINE_OVERSEAS=http://soo.trade.great:8008/selling-online-overseas/; \
	export DIRECTORY_CONSTANTS_URL_FIND_A_SUPPLIER=http://supplier.trade.great:8005/; \
	export DIRECTORY_CONSTANTS_URL_INVEST=http://invest.trade.great:8012/; \
	export DIRECTORY_CONSTANTS_URL_SINGLE_SIGN_ON=http://sso.trade.great:8004/; \
	export RECAPTCHA_PUBLIC_KEY=6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI; \
	export RECAPTCHA_PRIVATE_KEY=6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe; \
	export DIRECTORY_CH_SEARCH_CLIENT_API_KEY=debug; \
	export DIRECTORY_CH_SEARCH_CLIENT_BASE_URL=http://127.0.0.1:8012; \
	export DIRECTORY_FORMS_API_BASE_URL=http://forms.trade.great:8011; \
	export DIRECTORY_API_CLIENT_BASE_URL=http://api.trade.great:8000; \
	export DIRECTORY_CONSTANTS_URL_INVESTMENT_SUPPORT_DIRECTORY=http://supplier.trade.great:8005/investment-support-directory/\
	export DIRECTORY_API_CLIENT_API_KEY=debug; \
	export STORAGE_CLASS_NAME=local-storage; \
	export REDIS_URL=redis://localhost:6379; \
	export FEATURE_REQUEST_VERIFICATION_ENABLED=true; \
	export FEATURE_NEW_PROFILE_ADMIN_ENABLED=true


DEBUG_TEST_SET_ENV_VARS := \
	export EXPORTING_OPPORTUNITIES_API_BASE_URL=https://staging-new-design-eig.herokuapp.com/; \
	export EXPORTING_OPPORTUNITIES_API_SECRET=debug; \
	export EXPORTING_OPPORTUNITIES_SEARCH_URL=https://opportunities.export.great.gov.uk/opportunities; \
	export GET_ADDRESS_API_KEY=debug; \
	export DIRECTORY_FORMS_API_API_KEY=debug; \
	export DIRECTORY_FORMS_API_SENDER_ID=debug; \
	export URL_PREFIX_DOMAIN=http://testserver

debug_webserver:
	$(DEBUG_SET_ENV_VARS) && $(DJANGO_WEBSERVER)

debug_pytest:
	$(DEBUG_SET_ENV_VARS) && \
	$(DEBUG_TEST_SET_ENV_VARS) && \
	$(COLLECT_STATIC) && \
	$(PYTEST)

debug_test:
	$(DEBUG_SET_ENV_VARS) && \
	$(DEBUG_TEST_SET_ENV_VARS) && \
	$(COLLECT_STATIC) && \
	$(PYTEST)  && \
	$(FLAKE8)

debug_manage:
	$(DEBUG_SET_ENV_VARS) && ./manage.py $(cmd)

debug_shell:
	$(DEBUG_SET_ENV_VARS) && ./manage.py shell

debug: test_requirements debug_test

compile_requirements:
	pip-compile requirements.in
	pip-compile requirements_test.in

upgrade_requirements:
	pip-compile --upgrade requirements.in
	pip-compile --upgrade requirements_test.in

compile_css:
	./node_modules/.bin/gulp sass

watch_css:
	./node_modules/.bin/gulp sass:watch

.PHONY: build clean test_requirements debug_webserver debug_test debug heroku_deploy_dev heroku_deploy_demo
