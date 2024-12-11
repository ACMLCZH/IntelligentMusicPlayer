# myapp/tests/test_userfav.py
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from myapp.models import UserFav, Favlist, Song


class UserFavViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.other_user = User.objects.create_user(
            username="otheruser", password="otherpassword"
        )
        self.url = reverse(
            "userfav"
        )  # Ensure this matches the name='userfav' from urls.py
        self.client = APIClient()

    def test_unauthenticated_access(self):
        """
        Unauthenticated users should not be able to access the userfav endpoint.
        """
        response = self.client.get(self.url)
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
            f"Expected 401 or 403, got {response.status_code}",
        )

    def test_authenticated_user_get_without_existing_userfav(self):
        """
        If UserFav does not exist for an authenticated user, it should be created automatically.
        Also, a default Favlist named 'My favorites' should be created.
        """
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the userfav object now exists
        user_fav = UserFav.objects.filter(user=self.user).first()
        self.assertIsNotNone(user_fav, "UserFav should have been created.")

        # Check that a default favlist named 'My favorites' was created and associated
        favlists = user_fav.favlists.all()
        self.assertEqual(favlists.count(), 1)
        self.assertEqual(favlists.first().name, "My favorites")

        # Check response structure
        self.assertIn("favlists_detail", response.data)
        self.assertEqual(response.data["favlists_detail"][0]["name"], "My favorites")

    def test_authenticated_user_get_with_existing_userfav(self):
        """
        If UserFav already exists for a user, just return it along with its favlists.
        """
        # Create a userfav and favlist manually
        user_fav = UserFav.objects.create(user=self.user)
        favlist = Favlist.objects.create(name="Custom List", owner=self.user)
        user_fav.favlists.add(favlist)

        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check returned data
        self.assertIn("favlists_detail", response.data)
        self.assertEqual(len(response.data["favlists_detail"]), 1)
        self.assertEqual(response.data["favlists_detail"][0]["name"], "Custom List")

    def test_post_userfav_when_already_exists(self):
        """
        Attempting to POST a new UserFav when one already exists should fail.
        """
        UserFav.objects.create(user=self.user)

        self.client.login(username="testuser", password="testpassword")
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("UserFav already exists for this user.", str(response.data))

    def test_post_userfav_when_not_exists(self):
        """
        POST should create a new UserFav if none exists, and assign it to the user.
        """
        self.client.login(username="otheruser", password="otherpassword")
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user_fav = UserFav.objects.get(user=self.other_user)
        self.assertIsNotNone(user_fav)
        self.assertEqual(response.data["user"], self.other_user.pk)
        # The response won't contain the default favlist since default creation happens on GET.
        # For POST, we are just creating a blank userfav.

    def test_put_userfav(self):
        """
        Update the user's UserFav by assigning a new Favlist. This simulates adding or modifying favlists via PUT.
        """
        # Setup: create UserFav and a Favlist
        user_fav = UserFav.objects.create(user=self.user)
        favlist = Favlist.objects.create(name="New Favlist", owner=self.user)

        self.client.login(username="testuser", password="testpassword")
        # PUT with favlists data
        data = {"favlists": [favlist.id]}
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user_fav.refresh_from_db()
        self.assertIn(favlist, user_fav.favlists.all())

    def test_patch_userfav(self):
        """
        Partial update the user's UserFav by adding another Favlist.
        """
        user_fav = UserFav.objects.create(user=self.user)
        favlist1 = Favlist.objects.create(name="List 1", owner=self.user)
        user_fav.favlists.add(favlist1)

        favlist2 = Favlist.objects.create(name="List 2", owner=self.user)

        self.client.login(username="testuser", password="testpassword")
        data = {"favlists": [favlist1.id, favlist2.id]}
        response = self.client.patch(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user_fav.refresh_from_db()
        self.assertIn(favlist2, user_fav.favlists.all())

    def test_delete_userfav(self):
        """
        Deleting the UserFav should remove it from the database.
        """
        user_fav = UserFav.objects.create(user=self.user)
        self.client.login(username="testuser", password="testpassword")
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(UserFav.objects.filter(user=self.user).exists())
