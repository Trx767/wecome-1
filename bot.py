import http.server
import json
import logging
import os
import random
import re
import time
import urllib.parse
import urllib.request

logging.basicConfig(level=logging.INFO)

PORT = int(os.environ.get("PORT", 10000))
TOKEN = os.getenv("TOKEN", "8668928237:AAEEdsgiEz8jNBwLlkTxbSXXro33568-OCg")
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL")

user_warns = {}
go_enabled = {}

MEMBER_STICKER_ID = (
    "CAACAgUAAxkBAAESBaZqyogu8kKadNqxN3T1Uv7dcxI2sgACgCEAAtp_KVde-glYrCtWNT0E"
)
LEAVE_STICKER_ID = (
    "CAACAgUAAxkBAAESBclqywzRE3mY_0B0mFsiDzdhVx32fgACYhAAAtltiVaBcjx4byu5lj0E"
)

INSULT_MESSAGES = [
    "အပေါစားဖာသည်မ နင့်လင်လီး ပြေးမစုပ်ရလို့ ဂါနေတာလား",
    "မင်းရဲ့စိတ်ဓာတ်ကိုပြုပြင်အကျင့်ဆိုးတွေရှင်းထုတ်နောက်ကွယ်ကနေ foul ထုမကောင်ဘူးသူများအကြောင်းကိုဆတ်မဆိုနဲ့မင်းအလုပ်ကိုယ်မင်းလူပ်",
    "မင်းကိုဘယ်သူမေးလိုက်တာလည်း စောက်ဖာသည်မသား",
    "ဖာသည်သားသေချင်တာလား",
    "ဘယ်လိုအထင်နဲ့မင်းကိုယ်မင်းဆိုလ်ရှယ်ဂေါ့လို့ထင်တာလည်းငါ့အမြင်မှာသေးသေးလေးမင်းကကျွန်ပိန်းခြေမစုပ်ပါလားရောယောင်နေတာငပိန်းလိပ်လိုးမသားနှေးလိုက်တာမြန်ရေးပြီးကို",
    "ပေးမဖားဘူးနော် မအေလိုး အခြောက်မ နာနာ ကိုက်ပြ ကြွက်မသား",
    "ဆက်ရိုက်လေ",
    "ရိုက်လေဟ",
    "ဖာသယ်မသား",
    "မင်းအမေဖာတန်းမှာဆို ငါလိုးမကုလားမင်းအမေသေဘီဆို နွားမသား",
    "အိမ်‌ေမြာင်လိုးမသား",
    "မအေလိုးကလဲနဲနဲပဲစရသေးတယ်လောင်နေဘီ",
    "ဖာသည်မသားမင်းအမေသေလို့အူမြူးနေတာလား",
    "အမ်းဟုတ်တယ်လေ ငါနိုင်တယ်",
    "မင်းအမေစပတ်ကိုမော်တာတပ်လိုးပြီးစပိုက်တာမန်းလိုကြိုးဆွဲလိုးမှာငါလိုးမဖာသယ်မဖားအိုမဖာပျက်မခွေးမနွားမသား",
    "လိပ်နဲ့တက်လိုးလို့ထွက်လာတဲ့ကောင်ကြနေတာဘဲ",
    "ညီလိုင်းမကောင်းဘူးလား ဘာလဲ ဆင်းရဲလို့လား",
    "မင်းအမေဖင်ခံတာကျွမ်းတယ်",
    "အပြောကောင်းတယ်ဖင်ခံပလား",
    "ချေပနိုင်စွမ်းမရှိ",
    "မင်းကိုကောင်းချီးပေးပြီးဖင်လိုးမှာလေစောက်ကုလား",
    "မင်းရုပ်ကမဒိန်းကောင်ရုပ်နဲ့ အနူတောမှာပဲလူချောလုပ်ရမယ်ခွေးမသားရွှာနေပြီရောဖြေနေတာလား",
    "ငါလိုးမစောက်တောသား",
    "မင်းအမေဖာသည်မအေကိုက်လို့ဝလုးချီးသုတ်ရမ်းတာလား",
    "ငါကလမ်းမတော်မှာဆျာလေမင်းကတော့ခွေးသာပေါ့",
    "တယ်လီဂရမ်မှာငါအမြန်ဆုံးကွသိဖို့",
    "ဟိတ်ခွေးမင်းငါ‌ဆဲသလိုပြန်ဆဲတာလား",
    "ခွေးရူးပြန်နေတာလား ကာကွယ်ဆေးထိုးပေးကမလားမင်းကို",
    "ဆရာခေါ်",
    "ငါလိုးမခွေးဆဲရင်ငြိမ်ခံခုန်မကိုက်နဲ့",
    "ခွေးမသားကလဲငိုဖြဲဖြဲဖြစ်နေဘီဟ",
    "ငါလိုးမသား မင်းစာဘာအဓိပ္ပာယ်မှကိုမရှိဘူး စောက်ပညာမဲ့",
    "မင်းဆရာငါဆိုတာလက်ခံတာလား",
    "ဘောမတင်းနေတာလားတင်းနေရင်ဖင်ခံလိုက်",
    "ငဒူးလာရင်အကုန်ပြေးကြတာပဲ",
    "နှမလိုးလေး",
    "ယေရှူကိုးကွယ်တဲ့ကုလားဟလီးဘဲ မင်းအမေဖာသည်မအေကိုက်လို့ဝလုးချီးသုတ်ရမ်းတာလား",
    "ဟိတ်ကောင်",
    "ခွေးမသားချီူပေတဲ့လက်နဲ့ ရွေခွက်ကိုနိုက်ချင်တာလား",
    "မင်းအမေကိုမင်းဖေကလိင်မဆက်ဆံတော့မင်းအမေကသူများလိုးခိုင်းရတာဟ",
    "မင်းအမေကိုငါဆားသိပ်ပြီးလိုးလိုက်လို့ရှောသွားပြီရဖ",
    "ငါမလိုးပါ",
    "ငါလိုးမဘောမသေမယ် ငနူ မင်းမျေသတာပါဟင မုသေမယ်ဘောမကိုက်",
    "မင်းအမေဗစ်ခိုးပြီးရှုတာဆို",
    "မင်းအမေတညလွတ်လိုက်လေ ဖုန်းပြင်ခပေးမယ်လေ",
    "မင်းလိုလဒူကို ငါကဘာအကြောင်းပြချက်နဲ့မေးပေးရမာ ငါမေးတာခံချင်ရင် ငါ့ဘောလာမလေ",
    "ဟုတ်တယ်ဟကုလားမဆိုတာမင်းအမ",
    "စောက်အထာကျနည်းသင်ပေးမယ်ဖေဖေခေါ်",
    "မင်းအဖေကဂေးဆိုညီ",
    "စောက်စုန်းလားလီးစုန်းလားလီးစုပ်စုန်းလားဟ",
    "ရိုက်ဟ",
    "စောက်ဘောမ",
    "ကြမ်းခြင်တာလား ညေးက မင်းစောက်ဆင့်ကအောက်ခြေမာ ဖုံသုတ်အဝတ်နဲ့ ခြေနင်းခုံသာသာပဲရှိတယ် ကိုမေကိုလိုးကြီးရ",
    "သခင်ငဒူးကမြတ်တယ်လေ",
    "စောက်ရမ်းအာထုနေမယ့်အစားမင်းအဖေကိုmaster bateဘိတ်လုပ်ပေးလိုက်ပါလားမင်းမိဘလိုးမရဲ့",
    "ငါမြန်နေတာကိုကြည့်ပြီးထူးဆန်းနေလား တပည့်😂👌",
    "နွားမသားခိုးငိုတာလားဟ",
    "ပြေးထား",
    "စာတွေကလဲလိပ်တက်လိုးလို့ထွက်လာတဲ့ကောင်ကျနေတာပဲ",
    "မင်းအမေ ဂွေးစိ ဆိုက်ကားစမုတ်တံ စိုက်သေတာ ငါတို့မသိဘူးလေ မအေလိုးရ",
    "သောက်ကုလား သေချင်တာလား စောက်သုံးမကျဘူး မအေလိုး မင်းအမေရောသေပီးလား မင်းအဖေပါပေးတယ် သွားခေါ်သွား",
    "ကိုမေလိုးညတစ်ချို့ကောင်တွေငါနယ်မြေထဲကိုလူသစ်တွေကိုအမြဲခေါ်လာတယ်",
    "မင်းအမေဖာသည်မကြီးကိုလမ်းထိပ်မှာတွေ့ခဲ့တယ်",
    "မအေလိုးမင်းကိုဆဲတယ် မင်းမိဘနှမငါတက်လိုး",
    "ငါလိုးမသားမင်းလို stt တွေရှိလို့မြန်မာနိုင်ငံမတိုးတက်တာ",
    "မင်းစော်ဖင်ကြီးကိုက်ဆွဲပစ်မယ်",
    "ဒိုင်ဆိုဆောလိုးမသား",
    "မင်းအမေအိမ်လွှတ်လိုက်ငါလိုးမသားမင်းအမေငါ့လိင်တံကြီးကိုကြိုက်နေတာမသိဘူးလား",
    "ညီမင်းစာတွေထပ်နေတယ်ဘာလဲကြောက်လို့လား",
    "အေးဟုတ်တယ် မင်းအဖြစ်က ဆုတ်လဲ ဆူးစားလဲ ရုံးလေနစ်လေပဲ လက်မြှောက်အရှုံးပေးလိုက်တော့",
    "ဘာလဲမင်းစာမှန်အောင်ငါတက်လိုးပေးပြီးထွက်လာရင် မှန်မယ်ထင်တယ်",
    "မင်းမေလိုးဖာသည်မသား ဘိတ်မရလို့ခိုးငိုတာလားဟ Typingကြတော့လဲနှေးကွေးဖာပိန်းမသား ငါနင်းတာက ငါလိုးရင်ငြိမ်နေ",
    "မင်းအ‌မေငါတက်လိုးလို့လူဖြစ်လာတာ မအာနဲ့ခွေးမသားမေမေ့သားလားဟ မင်းကလဲ ငါဆဲလို့ငိုယိုပြီးသွားတိုင်ရတယ်တဲ့",
    "ကိုမေကိုလိုး ကြောက်ရင်ကြောက်တယ် လို့အခုကတည်းကပြော လျှော်ပေးမယ်🤞🥶",
    "စာတွေမမှန်ဘူးညီ မင်းအမေကျောင်းမထားနိုင်ဘူးလားဟ",
    "မင်းအမေကဖုန်းမှန်ကွဲနေတာမပြင်ပေးနိုင်တာဆို ပိုက်ဆံမရှိတာဆို",
    "ငါ က အမေလို မင်းကိုသနားနေမာ မဟုတ်ဘူး ဘစ်အုပ်ပြီး ဒစ်စုပ်ခိုင်းလိုက်မယ် 👌",
    "စာလုံးပေါင်းသတ်ပုံတောင်မမှန်ပဲဟောင်နေတာဟ",
    "ဖာသည်မသားပေတီပေစုတ်နဲ့ မင်းမေစပကို ပြေးယပ်ကွာ",
    "မင်အမေဗစ်ရာလေးတွေမြင်ပြီးလီးတောင်တာဆို",
    "မင်းနားမလည်နိုင်လောက်အောင် မင်းစောက်ဖြုတ်ဦးနှောက်နဲ့မတွေးနိုင်လောက်အောင် ငါ့အရေးအသားက စောက်ရမ်းအထာကျနေတာလား",
    "ငှက်လိုးမသား",
    "ငါလိုးမကုလားသေမယ်",
    "ပြေးထားပန်းခြံမှာ ချုံတိုးပြီး ကပ်တိုးလေးအကွက်ရွေနေတာလားဒီနေ့တစ်မွန်ထူးချား ရူးနည်းတစ်မျိုးလားမင်းတို့တစ်မိသားစုလုံးဧရာဝတီမြစ်ထဲရေဆင်းကူးတဲ့ကိစ္စငါတို့မသိချင်ဘူး ရဖဖာသည်မသား မင်းဖေရှမ်းကြီးလား ငပိရောင်းတာ ကိုယ်မေကိုယ်လိုး အနားမကပ်နဲ့ အပုပ်နံ့ရတယ်ငါမြေလျှိုးမိုးပျံရင်မင်းဘဝစုတ်ပျက်သက်သွားမယ်",
    "နှေးကွေးနေတာပဲစာတစ်လုံးနဲ့တစ်လုံးက",
    "ရေငုပ်တာလား",
    "ဟာဘောမ မင်းအမေမချစ်လို့လား",
    "အရိုးကိုက်",
]


def send_request(method, data):
  url = f"{BASE_URL}/{method}"
  try:
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as response:
      return json.loads(response.read().decode("utf-8"))
  except Exception as e:
    logging.error(f"API Error ({method}): {e}")
    return None


def send_message(chat_id, text, parse_mode="Markdown"):
  return send_request(
      "sendMessage",
      {"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
  )


def send_sticker(chat_id, sticker_id):
  return send_request(
      "sendSticker",
      {"chat_id": chat_id, "sticker": sticker_id},
  )


def delete_message(chat_id, message_id):
  return send_request(
      "deleteMessage",
      {"chat_id": chat_id, "message_id": message_id},
  )


def ban_chat_member(chat_id, user_id, until_date=None):
  data = {"chat_id": chat_id, "user_id": user_id}
  if until_date:
    data["until_date"] = until_date
  return send_request("banChatMember", data)


def unban_chat_member(chat_id, user_id):
  return send_request(
      "unbanChatMember",
      {"chat_id": chat_id, "user_id": user_id, "only_if_banned": True},
  )


def restrict_chat_member(chat_id, user_id, permissions, until_date=None):
  data = {"chat_id": chat_id, "user_id": user_id, "permissions": permissions}
  if until_date:
    data["until_date"] = until_date
  return send_request("restrictChatMember", data)


def get_chat_member(chat_id, user_id):
  res = send_request(
      "getChatMember",
      {"chat_id": chat_id, "user_id": user_id},
  )
  if res and res.get("ok"):
    return res.get("result")
  return None


def is_admin(chat_id, user_id):
  member = get_chat_member(chat_id, user_id)
  if member:
    return member.get("status") in ["administrator", "creator"]
  return False


def parse_time(time_str: str) -> int | None:
  match = re.match(r"^(\d+)([mhdw])$", time_str.lower())
  if not match:
    return None
  val, unit = int(match.group(1)), match.group(2)
  delta = 0
  if unit == "m":
    delta = val * 60
  elif unit == "h":
    delta = val * 3600
  elif unit == "d":
    delta = val * 86400
  elif unit == "w":
    delta = val * 604800
  return int(time.time()) + delta


class WebhookHandler(http.server.BaseHTTPRequestHandler):

  def do_GET(self):
    if self.path == "/":
      self.send_response(200)
      self.send_header("Content-type", "text/plain")
      self.end_headers()
      self.wfile.write(b"Telegram Bot Web Service is running!")
    else:
      self.send_response(404)
      self.end_headers()

  def do_POST(self):
    if self.path == "/webhook":
      content_length = int(self.headers.get("Content-Length", 0))
      post_data = self.rfile.read(content_length)
      try:
        update = json.loads(post_data.decode("utf-8"))
        handle_update(update)
      except Exception as e:
        logging.error(f"Error handling update: {e}")

      self.send_response(200)
      self.end_headers()
      self.wfile.write(b"OK")
    else:
      self.send_response(404)
      self.end_headers()


def handle_update(update):
  # Check chat_member updates (when someone leaves/joins)
  if "chat_member" in update:
    cm = update["chat_member"]
    chat_id = cm["chat"]["id"]
    old_status = cm["old_chat_member"].get("status")
    new_status = cm["new_chat_member"].get("status")

    if old_status in ["member", "restricted", "administrator"] and new_status == (
        "left"
    ):
      user_obj = cm["new_chat_member"]["user"]
      m_id = user_obj["id"]
      m_name = user_obj.get("first_name", "")
      mention = f"[{m_name}](tg://user?id={m_id})"

      ban_chat_member(chat_id, m_id)
      send_message(
          chat_id,
          f"{mention}\nထွက်ရင် ban တယ် မအေလိုး ပြန်မလာနဲ့",
      )
      send_sticker(chat_id, LEAVE_STICKER_ID)
    return

  if "message" in update:
    msg = update["message"]
    chat_id = msg["chat"]["id"]
    msg_id = msg["message_id"]
    user = msg.get("from", {})
    user_id = user.get("id")
    full_name = user.get("first_name", "") + (
        " " + user.get("last_name", "") if user.get("last_name") else ""
    )
    text = msg.get("text", "")
    reply_to = msg.get("reply_to_message")

    # Check left_chat_member in service messages as fallback
    if "left_chat_member" in msg:
      member = msg["left_chat_member"]
      m_id = member["id"]
      m_name = member.get("first_name", "")
      mention = f"[{m_name}](tg://user?id={m_id})"

      ban_chat_member(chat_id, m_id)
      send_message(
          chat_id,
          f"{mention}\nထွက်ရင် ban တယ် မအေလိုး ပြန်မလာနဲ့",
      )
      send_sticker(chat_id, LEAVE_STICKER_ID)
      return

    # New members welcome
    if "new_chat_members" in msg:
      for member in msg["new_chat_members"]:
        m_name = member.get("first_name", "")
        mention = f"[{m_name}](tg://user?id={member['id']})"
        send_message(
            chat_id, f"မင်္ဂလာပါ {mention} ရေ 👋\nGroup မှ နွေးထွေးစွာ ကြိုဆိုပါတယ်။"
        )
      return

    # Link filter
    link_regex = r"(https?://[^\s]+|t\.me/[^\s]+|telegram\.me/[^\s]+)"
    if text and re.search(link_regex, text, re.IGNORECASE):
      delete_message(chat_id, msg_id)
      key = (chat_id, user_id)
      current_warns = user_warns.get(key, 0) + 1
      user_warns[key] = current_warns
      mention = f"[{full_name}](tg://user?id={user_id})"

      if current_warns >= 3:
        ban_chat_member(chat_id, user_id)
        send_message(
            chat_id,
            f"⚠️ {mention} သည် Link (၃) ကြိမ် ပို့သောကြောင့် Group မှ"
            " Ban လိုက်ပါပြီ။",
        )
        user_warns.pop(key, None)
      else:
        send_message(
            chat_id,
            f"⚠️ {mention} Link ပို့ခွင့်မရှိပါ။\nသတိပေးချက်: ({current_warns}/3)"
            " ကြိမ် ရရှိထားပါသည်။ (၃) ကြိမ်ပြည့်ပါက Ban ခံရပါမည်။",
        )
      return

    parts = text.split()
    cmd = parts[0].split("@")[0] if parts else ""

    if cmd == "/start":
      send_message(
          chat_id,
          f"မင်္ဂလာပါ {full_name} ရေ 👋\nGroup မှ နွေးထွေးစွာ ကြိုဆိုပါတယ်။",
      )

    elif cmd == "/go":
      if not is_admin(chat_id, user_id):
        send_message(
            chat_id,
            "မင်းမာခွင့်ပြုချက်မရှိဘူး ဖာသယ်မသား\nသုံးချင်ရင်ဖေဖေခေါ son",
        )
        send_sticker(chat_id, MEMBER_STICKER_ID)
        return
      if chat_id in go_enabled and not go_enabled[chat_id]:
        return

      if reply_to and "from" in reply_to:
        target_user = reply_to["from"]
        target_id = target_user["id"]
        target_name = target_user.get("first_name", "")
      else:
        target_id = user_id
        target_name = full_name

      mention = f"[{target_name}](tg://user?id={target_id})"
      send_message(chat_id, f"သခင့်အလိုကျဖာသယ်မသားကိုဖင်စတင်လိုးပါတော့မယ်\n{mention}")

      insults = INSULT_MESSAGES.copy()
      random.shuffle(insults)
      for insult in insults:
        if chat_id in go_enabled and not go_enabled[chat_id]:
          break
        send_message(chat_id, f"{mention}\n{insult}")
        time.sleep(1.5)

    elif cmd == "/ungo":
      if not is_admin(chat_id, user_id):
        send_message(
            chat_id,
            "မင်းမာခွင့်ပြုချက်မရှိဘူး ဖာသယ်မသား\nသုံးချင်ရင်ဖေဖေခေါ son",
        )
        send_sticker(chat_id, MEMBER_STICKER_ID)
        return
      go_enabled[chat_id] = False
      send_message(chat_id, "ခွေးမသား အားလုံးငြိမ်းချမ်းစေ")

    elif cmd == "/rgo":
      if not is_admin(chat_id, user_id):
        send_message(
            chat_id,
            "မင်းမာခွင့်ပြုချက်မရှိဘူး ဖာသယ်မသား\nသုံးချင်ရင်ဖေဖေခေါ son",
        )
        send_sticker(chat_id, MEMBER_STICKER_ID)
        return
      go_enabled[chat_id] = True
      send_message(chat_id, "✅ `/go` ဖြင့် စာပို့ခြင်းကို ပြန်လည် ဖွင့်လိုက်ပါပြီ။")

    elif cmd == "/warn":
      if not reply_to or "from" not in reply_to:
        send_message(
            chat_id, "ကျေးဇူးပြု၍ Warn ပေးလိုသူ၏ မက်ဆေ့ချ်ကို Reply ပြန်၍ ပို့ပါ။"
        )
        return
      target_user = reply_to["from"]
      target_id = target_user["id"]
      target_name = target_user.get("first_name", "")
      key = (chat_id, target_id)
      current_warns = user_warns.get(key, 0) + 1
      user_warns[key] = current_warns
      mention = f"[{target_name}](tg://user?id={target_id})"

      if current_warns >= 3:
        ban_chat_member(chat_id, target_id)
        send_message(
            chat_id,
            f"⚠️ {mention} သည် Warn (၃) ကြိမ်ပြည့်သွားသောကြောင့် Ban လိုက်ပါပြီ။",
        )
        user_warns.pop(key, None)
      else:
        send_message(
            chat_id,
            f"⚠️ {mention} ကို Admin မှ Warn ပေးလိုက်ပါပြီ။ ({current_warns}/3)",
        )

    elif cmd == "/warns":
      target_user = (
          reply_to["from"] if (reply_to and "from" in reply_to) else user
      )
      target_id = target_user["id"]
      target_name = target_user.get("first_name", "")
      key = (chat_id, target_id)
      count = user_warns.get(key, 0)
      send_message(
          chat_id,
          f"👤 {target_name} ရရှိထားသော Warn အရေအတွက်: ({count}/3)",
      )

    elif cmd == "/resetwarns":
      if not reply_to or "from" not in reply_to:
        send_message(
            chat_id, "ကျေးဇူးပြု၍ Warn ပြန်ဖျက်ပေးလိုသူ၏ မက်ဆေ့ချ်ကို Reply ပြန်ပါ။"
        )
        return
      target_user = reply_to["from"]
      target_id = target_user["id"]
      target_name = target_user.get("first_name", "")
      key = (chat_id, target_id)
      user_warns.pop(key, None)
      send_message(
          chat_id, f"✅ {target_name} ၏ Warn များကို ပြန်လည် ဖျက်ပေးလိုက်ပါပြီ။"
      )

    # --- ROSE BOT MODERATION COMMANDS ---
    elif cmd == "/ban":
      if reply_to and "from" in reply_to:
        t_user = reply_to["from"]
        ban_chat_member(chat_id, t_user["id"])
        send_message(chat_id, f"❌ {t_user.get('first_name', '')} ကို Ban လိုက်ပါပြီ။")

    elif cmd == "/dban":
      if reply_to and "from" in reply_to:
        t_user = reply_to["from"]
        ban_chat_member(chat_id, t_user["id"])
        delete_message(chat_id, reply_to["message_id"])
        delete_message(chat_id, msg_id)

    elif cmd == "/sban":
      if reply_to and "from" in reply_to:
        t_user = reply_to["from"]
        ban_chat_member(chat_id, t_user["id"])
        delete_message(chat_id, msg_id)

    elif cmd == "/tban":
      if reply_to and "from" in reply_to and len(parts) > 1:
        t_user = reply_to["from"]
        until = parse_time(parts[1])
        if until:
          ban_chat_member(chat_id, t_user["id"], until_date=until)
          send_message(
              chat_id,
              f"⏳ {t_user.get('first_name', '')} ကို {parts[1]} ယာယီ Ban"
              " လိုက်ပါပြီ။",
          )

    elif cmd == "/unban":
      if reply_to and "from" in reply_to:
        t_user = reply_to["from"]
        unban_chat_member(chat_id, t_user["id"])
        send_message(
            chat_id, f"✅ {t_user.get('first_name', '')} ကို Unban လုပ်ပေးလိုက်ပါပြီ။"
        )

    elif cmd == "/mute":
      if reply_to and "from" in reply_to:
        t_user = reply_to["from"]
        restrict_chat_member(
            chat_id, t_user["id"], {"can_send_messages": False}
        )
        send_message(
            chat_id, f"🔇 {t_user.get('first_name', '')} ကို Mute လိုက်ပါပြီ။"
        )

    elif cmd == "/dmute":
      if reply_to and "from" in reply_to:
        t_user = reply_to["from"]
        restrict_chat_member(
            chat_id, t_user["id"], {"can_send_messages": False}
        )
        delete_message(chat_id, reply_to["message_id"])
        delete_message(chat_id, msg_id)

    elif cmd == "/smute":
      if reply_to and "from" in reply_to:
        t_user = reply_to["from"]
        restrict_chat_member(
            chat_id, t_user["id"], {"can_send_messages": False}
        )
        delete_message(chat_id, msg_id)

    elif cmd == "/tmute":
      if reply_to and "from" in reply_to and len(parts) > 1:
        t_user = reply_to["from"]
        until = parse_time(parts[1])
        if until:
          restrict_chat_member(
              chat_id, t_user["id"], {"can_send_messages": False}, until_date=until
          )
          send_message(
              chat_id,
              f"⏳ {t_user.get('first_name', '')} ကို {parts[1]} ယာယီ Mute"
              " လိုက်ပါပြီ။",
          )

    elif cmd == "/unmute":
      if reply_to and "from" in reply_to:
        t_user = reply_to["from"]
        restrict_chat_member(
            chat_id,
            t_user["id"],
            {
                "can_send_messages": True,
                "can_send_media_messages": True,
                "can_send_other_messages": True,
                "can_add_web_page_previews": True,
            },
        )
        send_message(
            chat_id,
            f"🔊 {t_user.get('first_name', '')} ကို Unmute လုပ်ပေးလိုက်ပါပြီ။",
        )

    elif cmd == "/kick":
      if reply_to and "from" in reply_to:
        t_user_obj = reply_to["from"]
        ban_chat_member(chat_id, t_user_obj["id"])
        unban_chat_member(chat_id, t_user_obj["id"])
        send_message(
            chat_id, f"👢 {t_user_obj.get('first_name', '')} ကို Kick လိုက်ပါပြီ။"
        )

    elif cmd == "/dkick":
      if reply_to and "from" in reply_to:
        t_user_obj = reply_to["from"]
        ban_chat_member(chat_id, t_user_obj["id"])
        unban_chat_member(chat_id, t_user_obj["id"])
        delete_message(chat_id, reply_to["message_id"])
        delete_message(chat_id, msg_id)


def set_webhook():
  if RENDER_EXTERNAL_URL:
    webhook_url = f"{RENDER_EXTERNAL_URL}/webhook"
    url = f"{BASE_URL}/setWebhook?url={urllib.parse.quote(webhook_url)}"
    try:
      with urllib.request.urlopen(url) as response:
        res = json.loads(response.read().decode("utf-8"))
        logging.info(f"Webhook set result: {res}")
    except Exception as e:
      logging.error(f"Failed to set webhook: {e}")


if __name__ == "__main__":
  set_webhook()
  server = http.server.HTTPServer(("0.0.0.0", PORT), WebhookHandler)
  logging.info(f"Starting Web Service server on port {PORT}...")
  server.serve_forever()
