#!/bin/bash

PROJECT_ROOT=../
IMAGE_PATH=../images
IMAGE=BatchCalculatorApp.dmg
APP=BatchCalculatorApp
APP_PATH=$PROJECT_ROOT/buildapp

mkdir $APP_PATH

cp $IMAGE_PATH/$IMAGE $APP_PATH
cd $APP_PATH

hdiutil convert $IMAGE -format UDSP -o $APP

rm $IMAGE 

hdiutil attach ${APP}.sparseimage

cp -r $PROJECT_ROOT/dist/batchcalc.app/Contents /Volumes/$APP/BatchCalculator.app/Contents

hdiutil detach /Volumes/$APP

hdiutil convert ${APP}.sparseimage -format UDBZ -o ${APP}.dmg
rm ${APP}.sparseimage
