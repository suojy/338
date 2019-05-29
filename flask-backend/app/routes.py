from flask import render_template, flash, redirect, request
from app import app
from app.forms import TwitterHandle
from utils.twitter_worker import TwitterWorker
from utils.feature_worker import FeatureWorker

from collections import Counter
import json
import os

# ellen   0.299910635630314   -0.19268990620758   0.49188117600401    0.536104548407424   0.152613595051368
# jones   0.386598906161264   -0.816132951125842  -0.00630991760763223    -0.272916121169616  -0.297895801599225
# justin  -0.0863439936710128 -0.027274289981541  0.647498495470014   0.369953545082055   0.592560201180955
# kanye   -0.422376018977781  -0.70700766348138   -0.1814592617385    -0.545910848864254  -0.478598523290196
# obama   0.364144449474829   0.782577476333631   -0.629466673644038  0.303257228323024   0.720172564961502
# trump   0.101371095973346   0.677445134474663   -0.69110912913034   -0.224822424033124  0.200991891561543

DEFAULT_SAMPLES = {
    '25073877': {'name': 'Donald Trump', 'handle': 'realDonaldTrump', 'user_id': 25073877,
                 'default_image': 'img/samples/thumbnails/trump.jpg'},
    '813286': {'name': 'Barack Obama', 'handle': 'barackobama', 'user_id': 813286,
               'default_image': 'img/samples/thumbnails/obama.jpg'},
    '47216804': {'name': 'Leslie Jones', 'handle': 'Lesdoggg', 'user_id': 47216804,
                 'default_image': 'img/samples/thumbnails/jones.jpg'},
    '4913077814': {'name': 'Kayne West', 'handle': 'officiaikanye', 'user_id': 4913077814,
                   'default_image': 'img/samples/thumbnails/west.jpg'},
    '15846407': {'name': 'Ellen DeGeneres', 'handle': 'TheEllenShow', 'user_id': 15846407,
                 'default_image': 'img/samples/thumbnails/ellen.jpg'},
    '27260086': {'name': 'Justin Bieber', 'handle': 'justinbieber', 'user_id': 27260086,
                 'default_image': 'img/samples/thumbnails/bieber.jpg'},
}

DEF_NUMBERED_SAMPLES = {
    'one': DEFAULT_SAMPLES['25073877'],
    'two': DEFAULT_SAMPLES['813286'],
    'three': DEFAULT_SAMPLES['47216804'],
    'four': DEFAULT_SAMPLES['4913077814'],
    'five': DEFAULT_SAMPLES['15846407'],
    'six': DEFAULT_SAMPLES['27260086'],
}
EVENT={
    102:["Hamilton","All month",
    "An American Musical is a sung-and-rapped through musical about the life of American Founding Father Alexander Hamilton, with music, lyrics and book by Lin-Manuel Miranda,inspired by the 2004 biography Alexander Hamilton by historian Ron Chernow.",
    "img/1.jpg" ],
    103:["Dames At Sea","Until June 2",
    "The musical is a parody of large, flashy 1930s Busby Berkeley-style movie musicals in which a chorus girl, newly arrived off the bus from the Midwest to New York City, steps into a role on Broadway and becomes a star.",
    "img/2.jpg"],
    104:["West Side Story","Until June 2",
    "This is a musical with book by Arthur Laurents, music by Leonard Bernstein and lyrics by Stephen Sondheim. It was inspired by William Shakespeare's play Romeo and Juliet.",
    "img/3.jpg"],
    105:["The Secret of the Biological Clock","Until June 2",
    "Sixteen-year-old Jasmine’s father has gone missing – but Jasmine just knows that she can convince former teen detective Eleanor Dawson to come out of retirement, she will be able to find him. The Secret of the Biological Clock is a whimsical riff on what happens to our favorite teen detectives when they grow up.",
    "img/4.png"],
    106:["Next to Normal","Until June 16",
    "This is a 2008 American rock musical with book and lyrics by Brian Yorkey and music by Tom Kitt. The story centers on a mother who struggles with worsening bipolar disorder and the effects that managing her illness has on her family.",
    "img/5.jpg"],
    107:["Mary Shelley's Frankenstein","Until Aug 4",
    "Mary Shelley’s unsettling story crackles to life as Victor Frankenstein must contend with his unholy creation. From the brain of Lookingglass Ensemble Member David Catlin (Moby Dick, Lookingglass Alice) comes a new, visceral adaptation of Frankenstein.",
    "img/6.png"],
    108:["Miracle","Until July 14",
    "Set against the backdrop of the Chicago Cubs 2016 Championship season, MIRACLE tells the story of a typical blue collar Chicago family and what it means to have faith and lose it and try to regain it again. ",
    "img/7.png"],
    109:["The Adventures of Augie March","Until June 9","Young Augie March is a product of the Great Depression: plucky, resourceful, searching for love, and striving to grow up and away from home. Through odd jobs and encounters with unique characters, Augie explores what it takes to succeed in the world as a true individual.",
    "img/8.png"],
    110:["Into the Breeches!","Until June 16","It’s 1942 and with the men off at war, the Oberon Play House is lacking its director and leading men. The season will be canceled… until the director’s wife rallies the troops at home for an all-female production. With the opportunity to move from the sidelines to centerstage, the women forge ahead with a spirit of collaboration, dauntless enthusiasm, and a belief in the power of art to move us forward. This surprisingly modern comedy proves that the show not only must, but will go on.",
    "img/9.png"],
    111:["Rent","","The show received its world premiere Off-Broadway at New York Theatre Workshop on February 13, 1996 to ecstatic reviews and transferred to Broadway on April 29, 1996. RENT is winner of the 1996 Tony Award® for Best Musical as well as the Pulitzer Prize for Drama. It is one of only five musicals to win both awards.",
    "img/10.jpg"],
    112:["The Princess And the Pea","Until Aug 9","Only a real Princess can feel a PEA under a stack of 20 mattresses! Meet Princess Penelope and her crazy friends-and find out if she can pass the ultimate Princess Test. You won't want to miss this great show-and the real 12-Foot bed! All CKC productions feature professional actors, colorful scenery and costumes, sing-along songs, and plenty of audience participation. This show is geared from children ages 2 to 10.",
    "img/11.jpg"],
    113:["Cirque du Solei - Volta","Until July 6",
    "Volta is the title of Cirque du Soleil's big top show which is themed around extreme sports. The show's storyline is about a game show host named Waz, who has lost touch with himself; he starts a personal quest to find his true self by going through his memories, after discovering a group of free spirits who encourage him during this process",
    "img/12.png"],
    114:["The Music Man","Until Aug 4",
    "The Music Man is a musical with book, music, and lyrics by Meredith Willson, based on a story by Willson and Franklin Lacey. The plot concerns con man Harold Hill, who poses as a boys' band organizer and leader and sells band instruments and uniforms to naive Midwestern townsfolk, promising to train the members of the new band.",
    "./data/img/13.jpg"],
}

#tweets[indices[1][1][0]]
def get_data_for_user(handle='', sample=False):
    data = {'name': '',
            'handle': handle,
            'profile_image': '',
            'category':[],
            'prediction': True,
            'tweets':[],
            }
   
    tw = TwitterWorker()
    fw=FeatureWorker()
    if not handle: data['handle'] = tw.default_handle
    if sample:
        data['handle'] = str(tw.getHandleFromUid(handle))
    
    # get profile info
    data.update(tw.get_profile(data['handle']))
    numbers=fw.get_category("./data/refinedtweets.csv",tw.get_tweets(data['handle']))[0]
    temp_tweets=tw.get_tweets(data['handle'])
    indices=fw.get_category("./data/refinedtweets.csv",tw.get_tweets(data['handle']))[1]
    
    for number in numbers:
        data['category'].append(EVENT[number[0]])
        
    for j in range(3):
        tweets=[]
        for i in range(3):
            tweets.append(temp_tweets[indices[j][0][i]])
        data['tweets'].append(tweets)
    
    return data

def get_topwords():
    data={
        "Hamilton":["indiana","et", "magnifique", "les", "emotions_pur", "pour", "region", "valparaiso", "town", "barbara20993343", 'sur', 'du', 'presents', 'announced', 'la', 'announces', 'le', 'sailing', 'moumoune_1'],
        "Dames At Sea":['sapphicscholar', 'heavensvault', 'dimplescanary', 'maverick', 'puppy', 'tmz', 'lizzens', 'tucoltd', 'sinfulsucc', 'westsidestory', 'meitoshirogane', 'copenkamizono', 'p_zippers', 'mtv', 'beyonc', 'americanidol', 'michaeljwoodard', 'worddancer21', 'ccicanine', 'rxtheatre'],
        "West Side Story":['andiearthur', 'comedy', 'https', 'athenaeum', 'bitter', 'tickets', 'chicagoplays', 'chicago', 'saw', 'sandstromjoanna', 'greenhouse2257', 'theatre', 'athenaeumtheatr', 'courtneymilan', 'bww_chicago', 'alicelfc4'],
        "The Secret of the Biological Clock":['toastsocko', 'michael', 'myownvelouria', 'degoldenllama1', '31i55a', 'nathaniel_m3', 'nigga', 'milieux_news', 'reallycody', 'game', 'tag_news', 'shebbi__', 'macatk_', 'rod31115', 'games', 'lowthaa', 'isidrosandoval8', 'qgcon', 'michaelevansb05', 'wooemmawatson'],
        "Next to Normal":['tom_six', 'choptopmoseley', 'atticuskelem', 'thecollector198', 'r0tten_teeth', 'horroraddictx', 'horror', 'char_stokely', 'frankenstein', 'denisegossett', 'stardustlola', 'emofrenchfries', 'book', '_rebeccaparham', 'girlsncorpses', 'myfriendsonfire', 'stokercon', 'thomassanders', 'hamillhimself'],
        "Mary Shelley's Frankenstein":['ilovvdaniel', 'theferryman', 'officestoh', 'elmoisnowgod', 'kinganditour', 'thatwannabeart2', 'floozyesq', '07', 'icymi', 'thelionking', 'picksinsix', 'gregpmiller', 'trump', 'futiledevicez', 'alum', 'srstoh', 'jillwinebanks'],
        "Miracle":['adamdalesandy', 'deannaraybourn', 'john_overholt', 'akhileshsharma1', 'sarahmaclean', 'kimsconvenience', 'chicollections', 'halfprice', 'jestom', 'rahul', 'avonbooks', 'uchicagolibrary', 'ogsaffron', 'mrdavehill', 'uchicago', 'the_book_queen', 'marked'],
        "The Adventures of Augie March":['breeches', 'scottmorrisonmp', 'suleikhasnyder', 'northlightthtr', 'ladyalicecassel', 'reginalupi_', 'landladies', 'alabamashakes', 'shorten', 'shakespeare', 'michaelwestbiz', 'capncrenn', 'mikecarlton01', 'billshortenmp', '3dclouds', 'ofknightiy', 'ofqueenlyrule', 'alistessaf'],
        "Into the Breeches!":['moh_alesawi', 'taylorcsmith__', 'pride', 'jazzyrgarcia', 'na', 'wanna1derland', 'southernhomo', 'rent', 'adk', 'kla2348', 'arifranny', 'nearlyillegal', 'jamescua2', 'arianagrande', 'juliajmoran', 'allenglean', 'bbynezza', 'sweetlikeari191'],
        "Rent":['thedempsterclan', 'protectpoppy', 'que', 'messsiejessie', 'silverqueldorei', 'curlywurlyfi', 'billingreeves', 'eustas', 'aquapoppie', 'inkandmagic', 'molinos1282', 'biryaniboyy', 'edgeicrd', 'ryanfoland', 'latenthaze', 'ichoriis', 'lexi'],
        "The Princess And the Pea":['challengerst', 'gamesack', 'cirque', 'alita', 'thegloved_one', 'starmike', 'lmaoooo', 'amomthatsleeps', 'hun', 'alitamovie', 'simoeliana', 'health', 'yaonlylivvonce', 'nctsmtown_127', 'justabxmom', 'bklynactivemama', 'bdisgusting', 'crissangel', 'alexabliss_wwe'],
        "Cirque du Solei - Volta":['armys', 'etaerealgguk', 'seokjin', 'itsmrcross', 'toto99com', '780613', 'tornado', 'namjoon', 'vernsanders', 'peacevibespromo', 'btsw_official', 'rt', 'jimin', 'bts', 'bts_twt', 'jungkook', 'yoongi'],
        "The Music Man":[],
    }
    return data 


@app.route('/', methods=["GET", "POST"])
@app.route('/index', methods=["GET", "POST"])
def index():
    form = TwitterHandle()
    if form.validate_on_submit():
        user_data = get_data_for_user(form.handle.data)
        return render_template('sample.html', form=form, sample_data=user_data, default_samples=DEF_NUMBERED_SAMPLES)
    return render_template('index.html', form=form, default_samples=DEF_NUMBERED_SAMPLES)


@app.route('/sample', methods=["GET", "POST"])
def sample():
    form = TwitterHandle()
    if request.method == 'POST':
        if form.validate_on_submit():
            user_data = get_data_for_user(form.handle.data)
            return render_template('sample.html', form=form, sample_data=user_data,
                                   default_samples=DEF_NUMBERED_SAMPLES)
        else:
            return render_template('index.html', form=form, default_samples=DEF_NUMBERED_SAMPLES)
    else:
        sample_handle = request.args.get('sample_handle')
        user_data = get_data_for_user(sample_handle, sample=True)
        return render_template('sample.html', form=form, sample_data=user_data, default_samples=DEF_NUMBERED_SAMPLES)

@app.route('/top', methods=["GET", "POST"])
def top():
    user_data = get_topwords()
    return render_template('top.html',sample_data=user_data)



