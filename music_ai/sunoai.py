import sys
import os
pp = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
print(pp)
sys.path.append(pp)

from suno import Suno, ModelVersions
from pydub import AudioSegment
from pydub.playback import play
from utils.tools import save_audio_to_local_file, save_image_to_local_file
from gpt4 import TempSong
from datetime import datetime
import io

# suno_cookie = "_cfuvid=BxMI5nhSxTZb0zIn.dLlJKtVRkjBs_TSE34D1TlGUCo-1731304443453-0.0.1.1-604800000; _ga=GA1.1.1420990047.1731304444; ajs_anonymous_id=8537c1a2-fd91-48e5-8d04-db54570e4eca; __client=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImNsaWVudF8yb2d3SThyeFB3SXJIMnZJbm55N0wzeGJXMG8iLCJyb3RhdGluZ190b2tlbiI6Im56eHVoeWdqMGFzaWlibmM1YWkxMmlwbGpyb2RkZThrMWRramV3a3cifQ.Ayw3M2YLimVlLQotG0a-Yxan77rGl9kFDC6NQtiwxrAbe_Kxr1c20vxvT3HhX0CphV9SpZvL5Zj5_l0IoZX2-RJEsSZ2IRv0c1JYRHViiibDx4CL7kkFnaW6AWaSaZWulv6FuXqSpCY9HODgetkcM7R9L_UY3X9oIi-hibf-HJkpnJaBF0N1wZRJMkK-YYwmzmtXY_oxeQS7qMzki-nrYIDZBf403O9FuisvS7huiUvdZJz9pMWodJrGhutia3KbjOEfolsViDCgaxxs-8rKuEusR63faYVrYBQhS_bOlBap4PmjUBDJDJBtkbJblXxnloVAt66AcNcSiwMQyIrwlA; __client_uat=1731304514; __client_uat_U9tcbTPE=1731304514; __cf_bm=2raT4eobM3qG9P.fKXB3PSnewiJWDvciXd8UswFuA50-1731310982-1.0.1.1-1_LjT8bMAyCcfOYqJvy6CapcbwEQH1gWMgxuFdjAtKfXWsRnmEYfU7Z6Kvfczlsq3mnBIdFtcIB1Wh1v3knuCQ; mp_26ced217328f4737497bd6ba6641ca1c_mixpanel=%7B%22distinct_id%22%3A%20%22ab504a97-a427-47ec-9d3b-b27bcea93f6d%22%2C%22%24device_id%22%3A%20%2219319c94e372cb-01186d7083d54c-4c657b58-13c680-19319c94e372cb%22%2C%22%24initial_referrer%22%3A%20%22%24direct%22%2C%22%24initial_referring_domain%22%3A%20%22%24direct%22%2C%22__mps%22%3A%20%7B%7D%2C%22__mpso%22%3A%20%7B%7D%2C%22__mpus%22%3A%20%7B%7D%2C%22__mpa%22%3A%20%7B%7D%2C%22__mpu%22%3A%20%7B%7D%2C%22__mpr%22%3A%20%5B%5D%2C%22__mpap%22%3A%20%5B%5D%2C%22%24search_engine%22%3A%20%22google%22%2C%22%24user_id%22%3A%20%22ab504a97-a427-47ec-9d3b-b27bcea93f6d%22%7D; _ga_7B0KEDD7XP=GS1.1.1731311038.2.1.1731311046.0.0.0"
suno_cookie = "_ga=GA1.1.686585545.1732064857; __cf_bm=6aVEsljYf74W0Qb0wrp6hzLu7aOZsiNlz0eRCIOnFho-1732064852-1.0.1.1-P4_.sVLdGqChd4ZpVgfHbaFzhiYfveVTLCKBlIMnhq_yu6L8xC40YeiGmCoUGfVKokyUez_4ioHiRC4wD5Q9nQ; _cfuvid=UMhycsSC4t7LplLa9Xbdz6mTsy4B0w4XNMPevyZycgU-1732064852810-0.0.1.1-604800000; ajs_anonymous_id=53a34eca-0244-4227-b1d6-72d78a071ade; __client=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImNsaWVudF8ycDVuWWkxaldsVmxIV3UzbGZjVlNiWE5EM3kiLCJyb3RhdGluZ190b2tlbiI6InZ2bmxvanRrOHAzaGpybGYwaGI3aTVyeHlybGtodWMyMnFydmJ6a2gifQ.HkZgY6F4kTECaSbyH4yOXd-40GDBGUkqzvGleekMg15OjFl0Ic5dXu0t_J8Ci2JUBLnKaTxFxlVt103K16DXXCZfRvrefDNbRFca-l8JCWGH7rWS69eSvIiYHt0d9C0yYrFoc8IPEkNbJFMqfjOD3voyddPY4Mo0MHkLZP8C-woZZV_jG5GMlTvqI731s56He4_YZoghsGbk7XEnS9SKTCiLy0SuyoVNE3HcRHx9U-_mv6nStFcgbYnA4-YBmbJd-O940ZM6aC6hMIVNs0bU-3_xgMqVZGgpLeehktJFBRp01J78XoBCunf6Hfy7IS-mtWRQgAEmjRCBAfmuJ2U2rw; __client_uat=1732064869; __client_uat_U9tcbTPE=1732064869; mp_26ced217328f4737497bd6ba6641ca1c_mixpanel=%7B%22distinct_id%22%3A%20%22ab504a97-a427-47ec-9d3b-b27bcea93f6d%22%2C%22%24device_id%22%3A%20%22193471c4767325-0a43dfe50c6214-4c657b58-13c680-193471c4767325%22%2C%22%24initial_referrer%22%3A%20%22%24direct%22%2C%22%24initial_referring_domain%22%3A%20%22%24direct%22%2C%22__mps%22%3A%20%7B%7D%2C%22__mpso%22%3A%20%7B%7D%2C%22__mpus%22%3A%20%7B%7D%2C%22__mpa%22%3A%20%7B%7D%2C%22__mpu%22%3A%20%7B%7D%2C%22__mpr%22%3A%20%5B%5D%2C%22__mpap%22%3A%20%5B%5D%2C%22%24user_id%22%3A%20%22ab504a97-a427-47ec-9d3b-b27bcea93f6d%22%7D; _ga_7B0KEDD7XP=GS1.1.1732064857.1.1.1732064906.0.0.0"

client = Suno(
    cookie=suno_cookie,
    model_version=ModelVersions.CHIRP_V3_5
)

def generate_songs(prompt):
    songs = client.generate(
        prompt=prompt,
        is_custom=False,
        wait_audio=True
    )

    song_list = []
    for song in songs:
        print(dir(song))
        local_song = TempSong(
            song.title, "SunoAI", "SunoAI Generation",
            datetime.now().year
        )
        song_list.append(local_song)
        save_audio_to_local_file(song.audio_url, local_song.audio_path)
        save_image_to_local_file(song.image_large_url, local_song.cover_path)
        local_song.print_info()

    return song_list

if __name__ == "__main__":
    # Play the first song in memory
    audio_data_list = generate_songs("Make a song of rap and hip-hop music, with a preference for hard-hitting beats, complex lyricism, and storytelling, from both classic and contemporary artists.")
    audio_data = audio_data_list[0]
    audio_segment = AudioSegment.from_file(io.BytesIO(audio_data), format="mp3")
    play(audio_segment)
