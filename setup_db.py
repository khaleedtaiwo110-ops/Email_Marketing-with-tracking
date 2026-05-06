import sqlite3

conn = sqlite3.connect("campaign.db")
cursor = conn.cursor()

# Add replied column
try:
    cursor.execute("ALTER TABLE contacts ADD COLUMN replied INTEGER DEFAULT 0")
    print("✅ 'replied' column added")
except:
    print("ℹ️ 'replied' already exists")

# Add opened column
try:
    cursor.execute("ALTER TABLE contacts ADD COLUMN opened INTEGER DEFAULT 0")
    print("✅ 'opened' column added")
except:
    print("ℹ️ 'opened' already exists")

conn.commit()
conn.close()

#Hi Micheal,

#Great connecting with you on your post earlier!

#I’m looking forward to that chat whenever the timing is right for you. I’ve been following your work and it aligns perfectly with how we approach travel operations—removing the chaos so the core strategy can scale.

#I’ll leave our cooperate review details here just to make things easier when you’re ready to dive in.