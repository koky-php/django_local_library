from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.fields import CharField
from django.db.models.fields.related import ForeignKey
from django.urls.base import reverse
from django.contrib.auth.models import User
from datetime import date
import uuid # Ce module est nécessaire à la gestion des identifiants unique (RFC 4122) pour les copies des livres

# Create your models here.

class Genre(models.Model):
    """Cet objet représente une catégorie ou un genre littéraire."""
    name = CharField(max_length=200, help_text='Enter a book genre (e.g. Science Fiction)')

    def __str__(self):
        """Cette fonction est obligatoirement requise par Django.
           Elle retourne une chaîne de caractère pour identifier l'instance de la classe d'objet."""
        return self.name

class Language(models.Model):
    """Model representing a Language (e.g. English, French, Japanese, etc.)"""
    name = models.CharField(max_length=200, help_text="Enter the book's natural language (e.g. English, French, Japanese etc.)")

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=200)

    # La clé étrangère (ForeignKey) est utilisée car elle représente correcte le modèle de relation en livre et son auteur :
    #  Un livre a un seul auteur, mais un auteur a écrit plusieurs livres.
    # Le type de l'objet Author est déclré comme une chaîne de caractère car
    # la classe d'objet Author n'a pas encore été déclarée dans le fichier
    author = models.ForeignKey('Author', on_delete=CASCADE)
    summary = models.TextField(max_length=1000, help_text="Enter a brief description of the book")
    isbn = models.CharField('ISBN', max_length=13, help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')
    
    # Le type ManyToManyField décrit correctement le modèle de relation entre un livre et un genre.
    # un livre peut avoir plusieurs genres littéraire et réciproquement.
    # Comme la classe d'objets Genre a été définit précédemment, nous pouvons manipuler l'objet.
    genre = models.ManyToManyField(Genre, help_text="Select a genre for this book")
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """Cette fonction est requise par Django, lorsque vous souhaitez détailler le contenu d'un objet."""
        return reverse('book-detail', args=[str(self.id)]) # return le lien d'un book

    def display_genre(self):
        """Create a string for the Genre. This is required to display genre in Admin."""
        return ', '.join(genre.name for genre in self.genre.all()[:3])

    display_genre.short_description = 'Genre'

class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=200)
    fullname = models.CharField(max_length=200, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('died', null=True, blank=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def get_absolute_url(self):
        """Returns the url to access a particular author instance."""
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        return f'{self.last_name}, {self.first_name}'

class BookInstance(models.Model):
    """Cet objet permet de modéliser les copies d'un ouvrage (i.e. qui peut être emprunté)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this particular book across whole library')
    book = models.ForeignKey('Book', on_delete=models.SET_NULL, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    LOAN_STATUS = (
        ('m', 'Maintenace'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )

    status = models.CharField(max_length=1, choices=LOAN_STATUS, blank=True, default="m", help_text='Book availability')
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['due_back']
        permissions = (("can_mark_returned", "Set book as returned"),)

    def __str__(self):
        ('m', 'Maintenace'),
        return f'{self.id} ({self.book.title})'

    @property
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back:
            return True
        return False