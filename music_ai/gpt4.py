from openai import OpenAI
import uuid
import os

# api_key = '8ebbc0ebe146462a939dfd4589b79e10'
data_folder = "data"

class TempSong:
    def __init__(self, title, artist, album, year):
        self.id = uuid.uuid4().hex
        self.song_folder = os.path.join(data_folder, str(self.id))
        self.audio_path = os.path.join(self.song_folder, "audio.mp3")
        self.cover_path = os.path.join(self.song_folder, "cover.png")
        self.title = title
        self.artist = artist
        self.album = album
        self.year = year

        os.makedirs(self.song_folder)
    
    def get_title(self):
        return self.title
    
    def get_artist(self):
        return self.artist
    
    def get_album(self):
        return self.album
    
    def get_year(self):
        return self.year
    
    def print_info(self):
        print(
            f"ID: {self.id}\n"
            f"Title: {self.title}\n"
            f"Artist: {self.artist}\n"
            f"Album: {self.album}\n"
            f"Year: {self.year}\n\n"
        )

client = OpenAI()
system_prompt = \
    "You are an expert music analyst. Your task is to evaluate a list of songs provided by the user "\
    "and summarize the music styles and properties that the user probably enjoys."

def make_song_prompt(songs):
    songs_info = "\n".join([
        f"Title: {song.get_title()}, Artist: {song.get_artist()}, Album: {song.get_album()}, Year: {song.get_year()}"
        for song in songs
    ])
    user_prompt = \
        "Here is a list of songs:\n"\
        f"{songs_info}\n"\
        "Based on these songs, summarize the music styles and properties that the user likely enjoys in one sentence. "\
        "Your answer should be recapitulatory and begin with \"The user likely enjoys...\"."
    print(user_prompt)

    answer = None
    while answer is None or not answer.startswith("The user likely enjoys") or len(answer) > 200:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "system",
                "content": system_prompt
            }, {
                "role": "user",
                "content": user_prompt
            }],
            temperature=0.7,
            max_tokens=100,
            top_p=1
        )
        answer = response.choices[0].message.content
    print(answer)
    return "Make a song of " + answer[23:]

if __name__ == "__main__":
    print(make_song_prompt([
        TempSong("Juicy", "The Notorious B.I.G.", "Ready to Die", 1994),
        TempSong("Lose Yourself", "Eminem", "8 Mile Soundtrack", 2002),
        TempSong("Sicko Mode", "Travis Scott", "Astroworld", 2018),
        TempSong("HUMBLE.", "Kendrick Lamar", "DAMN.", 2017),
    ]))