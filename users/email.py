from djoser import email

class ActivationEmail(email.ActivationEmail):
    def get_context_data(self):
        context = super().get_context_data()
        context["domain"] = "groc-ashy.vercel.app"
        context["protocol"] = "https"
        return context