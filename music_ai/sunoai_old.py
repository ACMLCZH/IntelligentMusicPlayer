# import sys
# import os
# pp = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
# print(pp)
# sys.path.append(pp)

from suno import Suno, ModelVersions
from pydub import AudioSegment
from pydub.playback import play
from utils.tools import save_audio_to_local_file, save_image_to_local_file
from gpt4 import TempSong
from datetime import datetime
import io

# suno_cookie = "_cfuvid=BxMI5nhSxTZb0zIn.dLlJKtVRkjBs_TSE34D1TlGUCo-1731304443453-0.0.1.1-604800000; _ga=GA1.1.1420990047.1731304444; ajs_anonymous_id=8537c1a2-fd91-48e5-8d04-db54570e4eca; __client=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImNsaWVudF8yb2d3SThyeFB3SXJIMnZJbm55N0wzeGJXMG8iLCJyb3RhdGluZ190b2tlbiI6Im56eHVoeWdqMGFzaWlibmM1YWkxMmlwbGpyb2RkZThrMWRramV3a3cifQ.Ayw3M2YLimVlLQotG0a-Yxan77rGl9kFDC6NQtiwxrAbe_Kxr1c20vxvT3HhX0CphV9SpZvL5Zj5_l0IoZX2-RJEsSZ2IRv0c1JYRHViiibDx4CL7kkFnaW6AWaSaZWulv6FuXqSpCY9HODgetkcM7R9L_UY3X9oIi-hibf-HJkpnJaBF0N1wZRJMkK-YYwmzmtXY_oxeQS7qMzki-nrYIDZBf403O9FuisvS7huiUvdZJz9pMWodJrGhutia3KbjOEfolsViDCgaxxs-8rKuEusR63faYVrYBQhS_bOlBap4PmjUBDJDJBtkbJblXxnloVAt66AcNcSiwMQyIrwlA; __client_uat=1731304514; __client_uat_U9tcbTPE=1731304514; __cf_bm=2raT4eobM3qG9P.fKXB3PSnewiJWDvciXd8UswFuA50-1731310982-1.0.1.1-1_LjT8bMAyCcfOYqJvy6CapcbwEQH1gWMgxuFdjAtKfXWsRnmEYfU7Z6Kvfczlsq3mnBIdFtcIB1Wh1v3knuCQ; mp_26ced217328f4737497bd6ba6641ca1c_mixpanel=%7B%22distinct_id%22%3A%20%22ab504a97-a427-47ec-9d3b-b27bcea93f6d%22%2C%22%24device_id%22%3A%20%2219319c94e372cb-01186d7083d54c-4c657b58-13c680-19319c94e372cb%22%2C%22%24initial_referrer%22%3A%20%22%24direct%22%2C%22%24initial_referring_domain%22%3A%20%22%24direct%22%2C%22__mps%22%3A%20%7B%7D%2C%22__mpso%22%3A%20%7B%7D%2C%22__mpus%22%3A%20%7B%7D%2C%22__mpa%22%3A%20%7B%7D%2C%22__mpu%22%3A%20%7B%7D%2C%22__mpr%22%3A%20%5B%5D%2C%22__mpap%22%3A%20%5B%5D%2C%22%24search_engine%22%3A%20%22google%22%2C%22%24user_id%22%3A%20%22ab504a97-a427-47ec-9d3b-b27bcea93f6d%22%7D; _ga_7B0KEDD7XP=GS1.1.1731311038.2.1.1731311046.0.0.0"
suno_cookie = "__cf_bm=jWAhfkCP6xUYGimYk__x7vgf2swdUsoHJX_dZarsYsU-1732656854-1.0.1.1-uwePM9Jc.avtVdoxQAQxRqmFpBC9HQbcB1szE.SQXFFV3BjLmdDdV.CS39JIh_U3WZ7XX5xzGsMTIO71QEYW1Q; _cfuvid=1TbA6KwNqwFI3hsZaR7AHPnekNEYvcq9Nd._Hkg9Xyo-1732656854104-0.0.1.1-604800000; _ga=GA1.1.144313835.1732656856; ajs_anonymous_id=8bdd7bc4-eda2-4ec4-9bc2-ea7eaa6f924b; __client=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImNsaWVudF8ycFA5VHZpWEl6aWlUNGJDakUwNGppZXhNZmQiLCJyb3RhdGluZ190b2tlbiI6ImRmZ2xtNjNldDkydW56NWhhb2xmcnA3YWZkcXhwbmpsYmJ6ODIxYnYifQ.oZ3y5NXc8Gk74_APOiyzkzx1GqhGPVneJk_4iZwasCzBPFLVROBkME6hZBbTf8k9G4BDK_BquhLPldC8Sj-xNqfM-CgxdYTqD4c5NNPMP2xn3ZL1QF1v7kLFvbHGwWOXkkZnhwsO9zvsgP4aU3c5tUFVLVJiioKPeyoWscu-9FsNWepwzwHKVOCFtv8TKhtGlZf4MZn9py6OqWR_WckHkbxQn-q3rORd6_bCQ3f8yeuLJa9iQGNpClWCOrOZKr-2PuvjNUnSuJNLU7D3Jvqc8YUhdA5Be8wLb49m4CkyuaB0Kjo6aJOK_-5B6UDjsFixeK0lt2lKPV0gB9YsGUObjw; __client_uat=1732656973; __client_uat_U9tcbTPE=1732656973; mp_26ced217328f4737497bd6ba6641ca1c_mixpanel=%7B%22distinct_id%22%3A%20%225783fc09-6ae3-4b92-9fe3-bda2f94fb2a0%22%2C%22%24device_id%22%3A%20%221936a657b94309-0a9799775674f1-4c657b58-13c680-1936a657b95309%22%2C%22%24initial_referrer%22%3A%20%22%24direct%22%2C%22%24initial_referring_domain%22%3A%20%22%24direct%22%2C%22__mps%22%3A%20%7B%7D%2C%22__mpso%22%3A%20%7B%7D%2C%22__mpus%22%3A%20%7B%7D%2C%22__mpa%22%3A%20%7B%7D%2C%22__mpu%22%3A%20%7B%7D%2C%22__mpr%22%3A%20%5B%5D%2C%22__mpap%22%3A%20%5B%5D%2C%22%24user_id%22%3A%20%225783fc09-6ae3-4b92-9fe3-bda2f94fb2a0%22%7D; _ga_7B0KEDD7XP=GS1.1.1732656856.1.1.1732657700.0.0.0"

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
