import requests
from flask import Flask, render_template, request, session
import re
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///profiles.db'  # Replace with your database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Optional: to suppress a warning
app.config['SECRET_KEY'] = 'omp02qrp05'
db = SQLAlchemy(app)


class Profiles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)

    def __repr__(self):
        return f"<Name {self.name}>"

@app.route("/delete/<int:profile_id>", methods=["POST"])
def delete_profile(profile_id):
    profile_to_delete = Profiles.query.get_or_404(profile_id)  # Get profile or return 404
    try:
        db.session.delete(profile_to_delete)  # Delete the profile
        db.session.commit()  # Commit changes
        return render_main_screen(saved_profiles=Profiles.query.all())  # Reload main screen
    except Exception as e:
        print(f"Error deleting profile: {e}")
        return render_main_screen(error="Error deleting profile.", saved_profiles=Profiles.query.all())

@app.route("/save", methods=["POST"])
def save_profile():
    seperateName = session.get("seperateName")
    print(seperateName)
    if seperateName:
        existing_profile = Profiles.query.filter_by(name=seperateName).first()
        if not existing_profile:
            new_profile = Profiles(name=seperateName)
            db.session.add(new_profile)
            db.session.commit()

        # Return the same as the index route
    return render_main_screen(summonerTotal=seperateName)


@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        summonerTotal = request.form['summonerTotal']
        session['seperateName'] = summonerTotal  # Store in session
        return render_main_screen(summonerTotal=summonerTotal)

    saved_profiles = Profiles.query.all()
    return render_main_screen(error=None, saved_profiles=saved_profiles)


main_amount = 5
filler = ""
with open("apikey.txt", "r") as file:
    apiKey = file.read().strip()  # strip() removes any leading/trailing whitespace

def render_main_screen(summonerTotal=None, error=None, saved_profiles=None):

    if saved_profiles is None:
        saved_profiles = Profiles.query.all()

    if not summonerTotal or "#" not in summonerTotal:
        return render_template("mainscreen.html",
                               error=error or "Invalid Summoner Name. Please include '#' in the format 'Name#Tag'",
                               saved_profiles=saved_profiles)

    summonerName, summonerTag = summonerTotal.split('#')
    try:
        puuid, capitalized = grabPUUID(summonerName, summonerTag, apiKey)
    except Exception as e:
        print(f"Error in grabChampNamesMastery: {e}")
        return render_template("mainscreen.html",
                               error="Failed to retrieve champion mastery data. Please try again.", saved_profiles=saved_profiles)

    icon = grabIcon(puuid, apiKey)
    champID = grabChampionID(puuid, apiKey)
    champkeydict = grabChampKeyDict()

    try:
        champNames, champMasteries, champNamesImages = grabChampNamesMastery(champID, champkeydict)
    except Exception as e:
        print(f"Error in grabChampNamesMastery: {e}")
        return render_template("mainscreen.html",
                               error="Failed to retrieve champion mastery data. Please try again.", saved_profiles=saved_profiles)

    divideGuide = chopMastery(champMasteries)
    choppedList = graphFive(champMasteries, divideGuide)

    profile_loaded = True

    firstelement, secondelement, thirdelement, fourthelement, fifthelement = choppedList
    firstmastery, secondmastery, thirdmastery, fourthmastery, fifthmastery = champMasteries[:5]
    champNames = champNames.split(",")
    firstname, secondname, thirdname, fourthname, fifthname = champNames[:5]
    firstnameimg, secondnameimg, thirdnameimg, fourthnameimg, fifthnameimg = champNamesImages[:5]


    return render_template("mainscreen.html",
                           firstelement=firstelement,
                           secondelement=secondelement,
                           thirdelement=thirdelement,
                           fourthelement=fourthelement,
                           fifthelement=fifthelement,

                           firstmastery=firstmastery,
                           secondmastery=secondmastery,
                           thirdmastery=thirdmastery,
                           fourthmastery=fourthmastery,
                           fifthmastery=fifthmastery,

                           firstname=firstname,
                           secondname=secondname,
                           thirdname=thirdname,
                           fourthname=fourthname,
                           fifthname=fifthname,

                           firstnameimg=firstnameimg,
                           secondnameimg=secondnameimg,
                           thirdnameimg=thirdnameimg,
                           fourthnameimg=fourthnameimg,
                           fifthnameimg=fifthnameimg,

                           capitalized=capitalized,
                           icon=f"{icon}.png",
                           profile_loaded=profile_loaded,
                           saved_profiles=saved_profiles
                           )


def find_id_by_key(json_data, key_value):
    for champion_name, champion_data in json_data["data"].items():
        if champion_data["key"] == str(key_value):  # Compare as string
            return champion_data["id"]
    return None

def chopMastery(mastery_list):
    if not mastery_list:
        return None

    firstElement = mastery_list[0]

    if firstElement == 0:
        return None

    divisor = firstElement / 600
    return divisor


def graphFive(mastery_list, divideGuide):
    choppedList = []
    for i in range(main_amount):
        divided = mastery_list[i] / divideGuide
        divided = round(divided) + 60
        choppedList.append(divided)
    return choppedList

def grabPUUID(summonerName, summonerTag, apiKey):
    response = requests.get(f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{summonerName}/{summonerTag}{apiKey}")
    data = response.json()
    puuid = data["puuid"]
    capitalized = data["gameName"]
    return puuid, capitalized

def grabIcon(puuid, apiKey):
    iconResponse = requests.get(f"https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}{apiKey}")
    dataicon = iconResponse.json()
    icon = dataicon["profileIconId"]
    return icon

def grabChampionID(puuid, apiKey):
    puuidresponse = requests.get(f"https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}{apiKey}")
    champID = puuidresponse.json()
    return champID

def grabChampKeyDict():
    champkey = requests.get(f"https://ddragon.leagueoflegends.com/cdn/14.24.1/data/en_US/champion.json")
    champkeydict = champkey.json()
    return champkeydict

def grabChampNamesMastery(champID, champkeydict):
    champion_names = []
    champion_names_img = []
    champion_masteries = []

    for i in range(main_amount):
        lolmain = champID[i]["championId"]
        lolmastery = champID[i]["championPoints"]
        champion_name = find_id_by_key(champkeydict, lolmain)
        if champion_name == "Wukong":
            champion_names_img.append(champion_name + "MonkeyKing.png")
        else:
            champion_names_img.append(champion_name + ".png")

        if champion_name:
            champion_name = re.sub(r"(\w)([A-Z])", r"\1 \2", champion_name)
            if champion_name == "Nunu":
                champion_name = "Nunu & Willump"
            if champion_name == "Jarvan I V":
                champion_name = "Jarvan IV"
            if champion_name == "K Sante":
                champion_name = "K'Sante"
            champion_names.append(champion_name)
            champion_masteries.append(lolmastery)

    output_string = ", ".join(champion_names)
    return output_string, champion_masteries, champion_names_img

def main():
    with app.app_context():
        db.create_all()
    app.run()




    
if __name__ == "__main__":
    main()

