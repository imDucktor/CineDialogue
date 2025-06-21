import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, font
from PIL import Image, ImageTk
import io
import re
import requests
from bs4 import BeautifulSoup
from imdb import Cinemagoer
import os

from config import (
    IMDB_TOP_MOVIES_URL,
    IMDB_BASE_URL,
    DARK_BG,
    LIGHT_BG,
    ACCENT_COLOR,
    TEXT_COLOR,
    BUTTON_COLOR,
    HOVER_COLOR
)
from generator import ContentGenerator
from utils import get_headers, save_dialogue_to_file, save_image_to_file

class MovieApp:
    def __init__(self, parent):
        self.root = parent
        self.root.title("PDA-226 Movie Dialogue and Image Generator")
        self.root.geometry("1100x700")
        self.root.minsize(900, 600)

        self.current_movie = None
        self.movies_data = []
        self.generator = ContentGenerator()

        self._apply_theme()
        self._configure_gui()
        self._populate_top_movies()

    def _apply_theme(self):
        """Apply visual theme to the application"""
        style = ttk.Style()
        style.theme_use('clam')

        style.configure('TFrame', background=LIGHT_BG)
        style.configure('TLabel', background=LIGHT_BG, foreground=TEXT_COLOR, font=('Segoe UI', 10))
        style.configure('TButton', background=BUTTON_COLOR, foreground='white', font=('Segoe UI', 10, 'bold'))
        style.map('TButton', background=[('active', HOVER_COLOR)])
        style.configure('TEntry', fieldbackground='white')
        style.configure('Treeview', background='white', fieldbackground='white', font=('Segoe UI', 10))
        style.map('Treeview', background=[('selected', ACCENT_COLOR)])

        self.heading_font = font.Font(family='Segoe UI', size=12, weight='bold')
        self.movie_font = font.Font(family='Segoe UI', size=11)

        self.root.configure(background=LIGHT_BG)

    def _configure_gui(self):
        """Configure the GUI layout and components"""
        self.paned_window = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left frame - Movie selection
        self._create_movie_selection_frame()

        # Right frame - Content generation
        self._create_content_generation_frame()

        # Status bar
        self.status_bar = ttk.Label(
            self.root,
            text="Ready",
            relief=tk.SUNKEN,
            anchor=tk.W,
            background=LIGHT_BG,
            foreground=TEXT_COLOR
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _create_movie_selection_frame(self):
        """Create the left frame with movie selection UI"""
        self.left_frame = ttk.Frame(self.paned_window, style='TFrame')
        self.paned_window.add(self.left_frame, weight=2)

        movie_title_frame = ttk.Frame(self.left_frame, style='TFrame')
        movie_title_frame.pack(fill=tk.X, padx=5, pady=(5, 0))

        title_label = ttk.Label(movie_title_frame, text="Top Movies", font=self.heading_font)
        title_label.pack(side=tk.LEFT, pady=5)

        refresh_button = ttk.Button(movie_title_frame, text="↻", width=3, command=self._populate_top_movies)
        refresh_button.pack(side=tk.RIGHT, pady=5)

        list_frame = ttk.Frame(self.left_frame, style='TFrame')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.movie_listbox = tk.Listbox(
            list_frame,
            selectmode=tk.SINGLE,
            font=self.movie_font,
            bg='white',
            fg=TEXT_COLOR,
            selectbackground=ACCENT_COLOR,
            selectforeground='white',
            activestyle='dotbox',
            relief=tk.FLAT,
            bd=1,
            highlightthickness=1,
            highlightcolor=ACCENT_COLOR,
            width=40
        )
        self.movie_listbox.pack(padx=0, pady=0, fill=tk.BOTH, expand=True)
        self.movie_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.movie_listbox.yview)
        self.movie_listbox.bind('<<ListboxSelect>>', self._on_movie_select)
        self.movie_listbox.bind('<Double-Button-1>', lambda e: self._generate_content())

    def _create_content_generation_frame(self):
        """Create the right frame with content generation UI"""
        self.right_frame = ttk.Frame(self.paned_window, style='TFrame')
        self.paned_window.add(self.right_frame, weight=3)

        # Input settings frame
        self._create_input_settings_frame()

        # Notebook with tabs
        self._create_notebook()

    def _create_input_settings_frame(self):
        """Create the input settings frame with entry fields"""
        self.input_frame = ttk.Frame(self.right_frame, style='TFrame')
        self.input_frame.pack(padx=5, pady=5, fill=tk.X)

        input_title = ttk.Label(self.input_frame, text="Generation Settings", font=self.heading_font)
        input_title.grid(row=0, column=0, columnspan=5, sticky=tk.W, padx=5, pady=(5,10))

        ttk.Label(self.input_frame, text="Number of Characters:", anchor=tk.E).grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        self.char_entry = ttk.Entry(self.input_frame)
        self.char_entry.insert(0, "2")  # Default value
        self.char_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W+tk.E)

        ttk.Label(self.input_frame, text="Dialogue Length (words):", anchor=tk.E).grid(row=1, column=2, padx=5, pady=5, sticky=tk.E)
        self.length_entry = ttk.Entry(self.input_frame)
        self.length_entry.insert(0, "500")  # Default value
        self.length_entry.grid(row=1, column=3, padx=5, pady=5, sticky=tk.W+tk.E)

        ttk.Label(self.input_frame, text="Location:", anchor=tk.E).grid(row=2, column=0, padx=5, pady=5, sticky=tk.E)
        self.location_entry = ttk.Entry(self.input_frame)
        self.location_entry.insert(0, "Interior")  # Default value
        self.location_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W+tk.E)

        ttk.Label(self.input_frame, text="Style:", anchor=tk.E).grid(row=2, column=2, padx=5, pady=5, sticky=tk.E)
        self.style_combobox = ttk.Combobox(self.input_frame, values=["Marvel", "Futuristic", "Cartoon", "Realistic"])
        self.style_combobox.set("Realistic")  # Default value
        self.style_combobox.grid(row=2, column=3, padx=5, pady=5, sticky=tk.W+tk.E)

        self.input_frame.columnconfigure(1, weight=1)
        self.input_frame.columnconfigure(3, weight=1)

        # Generate button
        self.generate_button = ttk.Button(
            self.input_frame,
            text="Generate Content",
            command=self._generate_content,
            style='TButton'
        )
        self.generate_button.grid(row=2, column=4, padx=5, pady=5, sticky=tk.E)

    def _create_notebook(self):
        """Create the notebook with tabs"""
        self.notebook = ttk.Notebook(self.right_frame)
        self.notebook.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        # Movie Details Tab
        self.details_tab = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(self.details_tab, text="Movie Details")

        self.details_text = scrolledtext.ScrolledText(
            self.details_tab,
            wrap=tk.WORD,
            font=('Segoe UI', 11),
            bg='white',
            fg=TEXT_COLOR
        )
        self.details_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        self.details_text.config(state=tk.DISABLED)

        # Generated Dialogue Tab
        self.dialogue_tab = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(self.dialogue_tab, text="Generated Dialogue")

        self.dialogue_text = scrolledtext.ScrolledText(
            self.dialogue_tab,
            wrap=tk.WORD,
            font=('Segoe UI', 11),
            bg='white',
            fg=TEXT_COLOR
        )
        self.dialogue_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        self.dialogue_text.config(state=tk.DISABLED)

        # Generated Image Tab
        self.image_tab = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(self.image_tab, text="Generated Image")

        self.image_frame = ttk.Frame(self.image_tab, style='TFrame')
        self.image_frame.pack(fill=tk.BOTH, expand=True)

        self.image_label = ttk.Label(self.image_frame)
        self.image_label.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

    def _populate_top_movies(self):
        """Fetch and populate the top movies list from IMDb"""
        try:
            self.set_status("Fetching movie list from IMDb...")

            response = requests.get(IMDB_TOP_MOVIES_URL, headers=get_headers())
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            movies_data = []

            # Find all movie links and titles
            links = soup.find_all('a')
            for link in links:
                href = link.get('href', '')
                if href.startswith('/title/tt') and '/tt' in href and link.text:
                    title = link.text.strip()
                    if title and len(title) > 1:
                        if re.match(r'^\d+\.', title):
                            title = re.sub(r'^\d+\.\s*', '', title)

                        movie_id = re.search(r'/title/(tt\d+)', href).group(1)
                        movie_url = f"{IMDB_BASE_URL}{href}"

                        if title and not any(m['title'] == title for m in movies_data):
                            movies_data.append({
                                'title': title,
                                'id': movie_id,
                                'url': movie_url
                            })

            self.movie_listbox.delete(0, tk.END)

            # Take top 10 movies for the list
            for i, movie in enumerate(movies_data[:10], start=1):
                self.movie_listbox.insert(tk.END, f"{i}. {movie['title']}")

                # Set alternating background colors for better readability
                if i % 2 == 0:
                    self.movie_listbox.itemconfig(i-1, {'bg': '#f5f5f5'})

            # Store the movies data for later use
            self.movies_data = movies_data
            self.set_status(f"Loaded {len(movies_data[:10])} top movies from IMDb")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch data from IMDb: {e}")
            self.set_status("Error fetching movies")

    def _on_movie_select(self, evt):
        """Handle movie selection from the list"""
        widget = evt.widget
        try:
            idx = int(widget.curselection()[0])
            selected_movie = self.movies_data[idx]

            self.set_status(f"Selected movie: {selected_movie['title']}")

            # Check if this is the same movie already displayed
            if self.current_movie and self.current_movie['id'] == selected_movie['id']:
                self.set_status(f"Movie '{selected_movie['title']}' already displayed")
                return

            self._fetch_and_display_movie_details(selected_movie)
        except IndexError:
            pass  # No selection
        except Exception as e:
            messagebox.showerror("Error", f"Error selecting movie: {e}")
            self.set_status("Error selecting movie")

    def _fetch_and_display_movie_details(self, movie_data):
        """Fetch and display movie details"""
        try:
            self.set_status(f"Fetching details for '{movie_data['title']}'...")
            movies = Cinemagoer().search_movie(movie_data['title'])
            if movies:
                movie = Cinemagoer().get_movie(movies[0].movieID)

                # Store current movie ID and title to prevent redundant fetches
                self.current_movie_id = {
                    'id': movies[0].movieID,
                    'title': movie_data['title']
                }
            # Fetch the movie page
            response = requests.get(movie_data['url'], headers=get_headers())
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract key details
            details = []
            detail_elems = soup.select('div.sc-bf57f3f2-0 a.ipc-link')
            if detail_elems:
                for detail in detail_elems:
                    details.append(detail.text.strip())
            # Poster Link
            poster_link = soup.select_one("a.ipc-lockup-overlay")["href"]
            # Rating
            rating_elem = soup.select_one('span.sc-d541859f-1')
            rating = rating_elem.text.strip() if rating_elem else 'Unknown'

            # Genre
            genres = []
            genre_elems = soup.select('div.ipc-chip-list a.ipc-chip')
            if genre_elems:
                for genre in genre_elems:
                    genres.append(genre.text.strip())

            # Director
            director = ""
            director_label = soup.find('span',
                                       class_='ipc-metadata-list-item__label ipc-metadata-list-item__label--btn ipc-btn--not-interactable',
                                       string='Director')
            if director_label:
                director_li = director_label.find_parent('li')
                director_link = director_li.find('a', class_='ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link')
                if director_link:
                    director = director_link.get_text(strip=True)

            # Cast
            cast = []
            cast_list = soup.select('div[data-testid="title-cast-item"]')
            for i, actor in enumerate(cast_list):
                if i >= 10:  # Get first 10 cast members
                    break
                actor_name = actor.select_one('a[data-testid="title-cast-item__actor"]')
                if actor_name:
                    cast.append(actor_name.text.strip())

            # Characters
            chars = []
            char_elems = soup.select('li.ipc-inline-list__item span.sc-cd7dc4b7-4')
            if char_elems:
                for char in char_elems:
                    chars.append(char.text.strip())

            # Storyline
            storyline = movie.get('plot outline', 'No storyline available.')

            # Store current movie
            self.current_movie = {
                'id': movie_data['id'],
                'title': movie_data['title'],
                'url': movie_data['url'],
                'year': details[0] if details else '',
                'rating': rating,
                'directors': director,
                'genres': genres,
                'cast': cast,
                'chars': chars,
                'storyline': storyline
            }

            # Format the details text
            details_text = f"🎬 Title: {movie_data['title']}\n\n"
            details_text += f"🖼 Poster: https://www.imdb.com{poster_link.split('?')[0]}\n\n"
            details_text += f"📍 Year: {details[0] if details else 'Unknown'}\n\n"
            details_text += f"🛑 Parental Guide(US): {details[1] if len(details) > 1 else 'Unknown'}\n\n"
            details_text += f"⭐ Rating: {rating}/10\n\n"
            details_text += f"🎭 Genres: {', '.join(genres) if genres else 'Unknown'}\n\n"
            details_text += f"🎬 Director: {director}\n\n"
            details_text += f"👥 Cast: {', '.join(cast) if cast else 'Unknown'}\n\n"
            details_text += f"👥 Characters: {', '.join(chars) if chars else 'Unknown'}\n\n"
            details_text += f"🔗 IMDb URL: {movie_data['url'].split('?')[0]}\n\n"
            details_text += f"📝 Storyline:\n{storyline}\n\n"

            self._update_details_text(details_text)
            self.set_status(f"Loaded details for '{movie_data['title']}'")

        except Exception as e:
            messagebox.showerror("Error", f"Error fetching movie details: {e}")
            self.set_status("Error fetching movie details")

    def _update_details_text(self, text):
        """Update the details text area with the given text"""
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete('1.0', tk.END)
        self.details_text.insert(tk.END, text)
        self.details_text.config(state=tk.DISABLED)

    def _generate_content(self):
        """Generate dialogue and image content"""
        try:
            num_characters = int(self.char_entry.get())
            dialogue_length = int(self.length_entry.get())
            location = self.location_entry.get()
            style = self.style_combobox.get()

            # Validate input
            if not (2 <= num_characters <= 4):
                messagebox.showerror("Input Error", "Number of characters must be between 2 and 4.")
                return

            selected_movie_index = self.movie_listbox.curselection()
            if not selected_movie_index:
                messagebox.showerror("Selection Error", "Please select a movie.")
                return

            movie_idx = selected_movie_index[0]
            selected_movie = self.movies_data[movie_idx]

            self.set_status(f"Generating content for '{selected_movie['title']}'...")

            if not self.current_movie or self.current_movie['id'] != selected_movie['id']:
                self._fetch_and_display_movie_details(selected_movie)

            # Get storyline
            storyline = self.current_movie.get('storyline', "No storyline available.")
            if storyline == "No storyline available.":
                messagebox.showerror("Error", "Storyline not available for this movie.")
                self.set_status("Error: Missing storyline")
                return

            char_names = self.current_movie.get('chars', [])

            while len(char_names) < num_characters:
                char_names.append(f"Character {len(char_names) + 1}")

            char_names = char_names[:num_characters]

            # Generate Dialogue with character names
            self.set_status("Generating dialogue...")
            dialogue = self.generator.generate_movie_dialogue(
                selected_movie['title'],
                storyline,
                char_names,
                num_characters,
                dialogue_length
            )
            self._display_dialogue(dialogue)
            self.notebook.select(1)

            # Generate Scene Description
            self.set_status("Generating scene description...")
            scene_description = self.generator.generate_scene_description(selected_movie['title'], storyline)

            # Generate Image with prompt
            self.set_status("Generating image...")
            characters_description = f"{num_characters} characters from the movie {selected_movie['title']}"

            image_bytes = self.generator.generate_movie_image(
                selected_movie['title'],
                scene_description,
                location,
                characters_description,
                style
            )

            if image_bytes:
                self._display_image(image_bytes)
                self.set_status("Content generation complete")
            else:
                self.set_status("Image generation failed")

        except ValueError:
            messagebox.showerror("Input Error", "Invalid input for number of characters or dialogue length.")
            self.set_status("Error: Invalid input values")
        except Exception as e:
            messagebox.showerror("Error", f"Error generating content: {e}")
            self.set_status(f"Error generating content: {str(e)[:50]}")

    def _display_dialogue(self, dialogue):
        """Display the generated dialogue in the text area"""
        self.dialogue_text.config(state=tk.NORMAL)
        self.dialogue_text.delete('1.0', tk.END)
        self.dialogue_text.insert(tk.END, dialogue)
        self.dialogue_text.config(state=tk.DISABLED)
        save_dialogue_to_file(dialogue)

    def _display_image(self, image_bytes):
        """Display the generated image"""
        if image_bytes:
            try:
                image = Image.open(io.BytesIO(image_bytes))

                max_width = 800
                max_height = 600
                width, height = image.size

                if width > max_width or height > max_height:
                    ratio = min(max_width / width, max_height / height)
                    new_width = int(width * ratio)
                    new_height = int(height * ratio)
                    image = image.resize((new_width, new_height), Image.LANCZOS)

                photo = ImageTk.PhotoImage(image)
                self.image_label.config(image=photo)
                self.image_label.image = photo  # Keep a reference!

                save_image_to_file(image_bytes)

                self.notebook.select(2)
            except Exception as e:
                print(f"Failed to display image: {e}")
                self.image_label.config(text="Failed to display image")
        else:
            self.image_label.config(text="Image generation failed.")

    def set_status(self, message):
        """Update the status bar message"""
        self.status_bar.config(text=message)
        self.root.update_idletasks()  # Force update
