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
    102:["Hamilton","All month" ],
    103:["Dames At Sea","Until June 2"],
    104:["West Side Story","Until June 2"],
    105:["The Secret of the Biological Clock","Until June 2"],
    106:["Next to Normal","Until June 16"],
    107:["Mary Shelley's Frankenstein","Until Aug 4"],
    108:["Miracle","Until July 14"],
    109:["The Adventures of Augie March","Until June 9"],
    110:["Into the Breeches!","Until June 16"],
    111:["Rent",""],
    112:["The Princess And the Pea","Until Aug 9"],
    113:["Cirque du Solei - Volta","Until July 6"],
    114:["The Music Man","Until Aug 4"],
}

def get_data_for_user(handle='', sample=False):
    data = {'name': '',
            'handle': handle,
            'profile_image': '',
            'category':[],
            'prediction': True,
            }

    tw = TwitterWorker()
    fw=FeatureWorker()
    if not handle: data['handle'] = tw.default_handle
    if sample:
        data['handle'] = str(tw.getHandleFromUid(handle))

    # get profile info
    data.update(tw.get_profile(data['handle']))
    number=fw.get_category(tw.get_tweets(data['handle']))
    data['category']=EVENT[number]
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





