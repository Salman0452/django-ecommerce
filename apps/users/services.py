from django.contrib.auth import get_user_model

User = get_user_model()


def register_user(email, password):
    """Create and return a new active user with the given email and password."""
    user = User.objects.create_user(
        username=email,
        email=email,
        password=password,
    )
    return user


def update_profile(user, first_name, last_name):
    """Update the user's first and last name and return the updated user."""
    user.first_name = first_name
    user.last_name = last_name
    user.save(update_fields=['first_name', 'last_name', 'updated_at'])
    return user
