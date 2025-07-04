import csv
import random
from faker import Faker
from datetime import datetime, timedelta
import uuid
import os

faker = Faker('pt_BR')
random.seed(42)
Faker.seed(42)

# Caminho dos arquivos
os.makedirs("data/raw", exist_ok=True)

# Parâmetros
NUM_USERS = 5000
NUM_CAMPAIGNS = 30
NUM_OPENS = 20000
NUM_BOUNCES = 2000
NUM_CLICKS = 10000
NUM_UNSUBSCRIBES = 500

# Helpers
def gerar_data_recente(dias=365):
    return faker.date_time_between(start_date=f"-{dias}d", end_date="now")

def gerar_link():
    secoes = ["promocoes", "produtos", "novidades", "destaques"]
    categorias = ["roupas", "calcados", "eletronicos", "moveis", "beleza", "livros"]
    return f"/{random.choice(secoes)}/{random.choice(categorias)}"

#---------------------------------------
# 1. USERS
#---------------------------------------
users = []
user_ids = []

for i in range(NUM_USERS):
    user_id = f"U{str(i+1).zfill(5)}"
    signup_date = gerar_data_recente(730)
    is_active = random.choices([True, False], weights=[0.8, 0.2])[0]
    unsubscribe_date = None if is_active else faker.date_time_between(start_date=signup_date, end_date="now")
    users.append([
        user_id,
        faker.name(),
        faker.email(),
        signup_date.strftime("%Y-%m-%d"),
        is_active,
        unsubscribe_date.strftime("%Y-%m-%d") if unsubscribe_date else ""
    ])
    user_ids.append(user_id)

with open("data/users.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["user_id", "name", "email", "signup_date", "is_active", "unsubscribe_date"])
    writer.writerows(users)

# ------------------------------
# 2. CAMPAIGNS
# ------------------------------
campaigns = []
campaign_ids = []

base_date = datetime.now() - timedelta(days=30)
for i in range(NUM_CAMPAIGNS):
    campaign_id = f"C{str(i+1).zfill(3)}"
    send_date = base_date + timedelta(days=i)
    subject = faker.catch_phrase()
    total_recipients = NUM_USERS
    campaigns.append([campaign_id, subject, send_date.isoformat(), total_recipients])
    campaign_ids.append((campaign_id, send_date))

with open("data/campaigns.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["campaign_id", "subject", "send_date", "total_recipients"])
    writer.writerows(campaigns)

# ------------------------------
# 3. EMAIL EVENTS (open + bounce)
# ------------------------------
email_events = []
opens = random.choices(user_ids, k=NUM_OPENS)
bounces = random.choices(user_ids, k=NUM_BOUNCES)

for user_id in opens:
    campaign_id, send_date = random.choice(campaign_ids)
    event_time = send_date + timedelta(minutes=random.randint(1, 180))
    email_events.append([
        str(uuid.uuid4()),
        user_id,
        campaign_id,
        "open",
        event_time.isoformat(),
        random.choice(["mobile", "desktop", "tablet"]),
        f"{faker.city()}/{faker.estado_sigla()}"
    ])

for user_id in bounces:
    campaign_id, send_date = random.choice(campaign_ids)
    event_time = send_date + timedelta(minutes=random.randint(1, 60))
    event_type = random.choices(["bounce_soft", "bounce_hard"], weights=[0.7, 0.3])[0]
    email_events.append([
        str(uuid.uuid4()),
        user_id,
        campaign_id,
        event_type,
        event_time.isoformat(),
        random.choice(["mobile", "desktop", "tablet"]),
        f"{faker.city()}/{faker.estado_sigla()}"
    ])

with open("data/email_events.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["event_id", "user_id", "campaign_id", "event_type", "event_time", "device_type", "location"])
    writer.writerows(email_events)

# ------------------------------
# 4. CLICK EVENTS
# ------------------------------
# Primeiro filtramos os eventos de abertura para cliques realistas
opens_filtrados = [e for e in email_events if e[3] == "open"]
clicados = random.sample(opens_filtrados, NUM_CLICKS)

clicks = []
for evento in clicados:
    event_id, user_id, campaign_id, _, open_time_str, *_ = evento
    open_time = datetime.fromisoformat(open_time_str)
    click_time = open_time + timedelta(seconds=random.randint(5, 1800))
    clicks.append([
        str(uuid.uuid4()),
        user_id,
        campaign_id,
        gerar_link(),
        click_time.isoformat()
    ])

with open("data/click_events.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["click_id", "user_id", "campaign_id", "link_clicked", "click_time"])
    writer.writerows(clicks)

# ------------------------------
# 5. UNSUBSCRIBE EVENTS
# ------------------------------
inativos = [u for u in users if not u[4]]  # is_active = False
unsubscribe_amostra = random.sample(inativos, min(NUM_UNSUBSCRIBES, len(inativos)))
reasons = ["emails demais", "irrelevante", "não lembro de me cadastrar", "outro motivo"]

unsubscribe_events = []
for u in unsubscribe_amostra:
    user_id = u[0]
    signup = datetime.strptime(u[3], "%Y-%m-%d")
    cancel_date = faker.date_time_between(start_date=signup, end_date="now")
    reason = random.choice(reasons)
    unsubscribe_events.append([user_id, cancel_date.isoformat(), reason])

with open("data/unsubscribe_events.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["user_id", "unsubscribe_date", "reason"])
    writer.writerows(unsubscribe_events)

print("✅ Todas as bases foram geradas com sucesso na pasta /data!")
