
#Startup AI to Gender and Emotion classifier

## Images from web app
<p float="left">
  <img src="/screenshots/home.JPG" width="50%"/>
  <img src="/screenshots/service.JPG" width="42%"/>
</p>

## Images portfolio
<p float="left">
  <img src="/screenshots/portfolio.JPG" width="50%"/>
  <img src="/screenshots/pagetest.JPG" width="42%"/>
</p>

## Images prediction web app
<p>
  <img src="/screenshots/uploadimage.JPG" width="75%"/>
  <img src="/screenshots/predict.JPG" width="75%"/>
</p>

## Instructions on testing the webapp

1. Go to https://startup-bonaeng.herokuapp.com/
2. Create account and login.
4. You're ready to upload your image and let it detect the lung disease for you.

## Introduction

The goal of this project is to create various machine learning based applications for various industrial sectors. With available MVP's interested can test the application and buy if they like or want to implement in any solution. The first algorithm classifies genres and emotions by image.


## Setup


- Install the requirements and setup the development environment.

	`make install && make dev`

- Create the database.

	`python manage.py initdb`

- Run the application.

	`python manage.py runserver`

- Navigate to `localhost:5000`.

## Configuration

The goal is to keep most of the application's configuration in a single file called `config.py`. I added a `config_dev.py` and a `config_prod.py` who inherit from `config_common.py`. The trick is to symlink either of these to `config.py`. This is done in by running `make dev` or `make prod`.

I have included a working Gmail account to confirm user email addresses and reset user passwords, although in production you should't include the file if you push to GitHub because people can see it. The same goes for API keys, you should keep them secret. You can read more about secret configuration files [here](https://exploreflask.com/configuration.html).

Read [this](http://flask.pocoo.org/docs/0.10/config/) for information on the possible configuration options.

Configure keys for payments via paypal and chose a environment sandbox or production in user.py and face.html.

