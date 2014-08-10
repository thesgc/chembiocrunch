from django.conf import settings
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView, View
from workflow.forms import UserLoginForm

class Login(FormView):
    form_class = UserLoginForm
    template_name = "login.html"
    logout = None
    def get(self, request, *args, **kwargs):
        # logout = None
        # if logout in kwargs:
        #     logout = kwargs.pop("logout")
        #     print logout
        redirect_to = settings.LOGIN_REDIRECT_URL
        '''Borrowed from django base detail view'''
        if self.request.user.is_authenticated():
            return HttpResponseRedirect(redirect_to)
        context = self.get_context_data(form=self.get_form(self.get_form_class()))
        context["logout"] = self.logout
        return self.render_to_response(context)


    def form_valid(self, form):
        redirect_to = settings.LOGIN_REDIRECT_URL
        auth_login(self.request, form.get_user())
        if self.request.session.test_cookie_worked():
            self.request.session.delete_test_cookie()
        return HttpResponseRedirect(redirect_to)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    @method_decorator(sensitive_post_parameters('password'))
    def dispatch(self, request, *args, **kwargs):
        request.session.set_test_cookie()
        return super(Login, self).dispatch(request, *args, **kwargs)

class Logout(View):
    def get(self, request, *args, **kwargs):
        auth_logout(request)
        return HttpResponseRedirect(settings.LOGOUT_REDIRECT_URL)