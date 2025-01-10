import json
import requests
from flask import Flask, render_template, request
from werkzeug.exceptions import BadRequest, abort
import re


app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':

        summonerTotal = request.form['summonerTotal']
        if not summonerTotal or "#" not in summonerTotal:
            # Instead of Flask's default "Bad Request" screen, render a custom page or error message
            return render_template("mainscreen.html",
                                   error="Invalid Summoner Name. Please include '#' in the format 'Name#Tag'")
        print(summonerTotal)
        summonerName, summonerTag = summonerTotal.split('#')
        try:
            puuid, capitalized = grabPUUID(summonerName, summonerTag, apiKey)
        except Exception as e:
            # Handle specific errors or log the exception
            print(f"Error in grabChampNamesMastery: {e}")
            return render_template("mainscreen.html",
                                   error="Failed to retrieve champion mastery data. Please try again.")

        icon = grabIcon(puuid, apiKey)

        champID = grabChampionID(puuid, apiKey)
        champkeydict = grabChampKeyDict()
        try:
            champNames, champMasteries, champNamesImages = grabChampNamesMastery(champID, champkeydict)
        except Exception as e:
            # Handle specific errors or log the exception
            print(f"Error in grabChampNamesMastery: {e}")
            return render_template("mainscreen.html",
                                   error="Failed to retrieve champion mastery data. Please try again.")

        divideGuide = chopMastery(champMasteries)
        choppedList = graphFive(champMasteries, divideGuide)

        firstelement = choppedList[0];
        secondelement = choppedList[1];
        thirdelement = choppedList[2];
        fourthelement = choppedList[3];
        fifthelement = choppedList[4];

        firstmastery = champMasteries[0];
        secondmastery = champMasteries[1];
        thirdmastery = champMasteries[2];
        fourthmastery = champMasteries[3];
        fifthmastery = champMasteries[4];

        champNames = champNames.split(",")

        firstname = champNames[0];
        secondname = champNames[1];
        thirdname = champNames[2];
        fourthname = champNames[3];
        fifthname = champNames[4];

        firstnameimg = champNamesImages[0];
        secondnameimg = champNamesImages[1];
        thirdnameimg = champNamesImages[2];
        fourthnameimg = champNamesImages[3];
        fifthnameimg = champNamesImages[4];


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
                               icon = f"{icon}.png"
                               )
    return render_template("mainscreen.html", summonerTotal=filler)

main_amount = 5
filler = ""
with open("apikey.txt", "r") as file:
    apiKey = file.read().strip()  # strip() removes any leading/trailing whitespace

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
    app.run()




    
if __name__ == "__main__":
    main()