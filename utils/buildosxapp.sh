#!/bin/bash

PROJECT_ROOT=/Users/lukaszmentel/Devel/batchcalculator
IMAGE_FILE=BatchCalculator.dmg
APP_NAME=BatchCalculator
WORKDIR=$PROJECT_ROOT/utils/buildapp

mkdir -p $WORKDIR
cd $WORKDIR

# create the image containing the app
hdiutil create -size 50m -fs HFS+ -srcfolder $PROJECT_ROOT/dist/BatchCalculator.app -volname $APP_NAME $IMAGE_FILE
# convert to sparseimage
hdiutil convert $IMAGE_FILE -format UDSP -o $APP_NAME
rm $IMAGE_FILE

# create the shortcut to Applications folder
hdiutil attach ${APP_NAME}.sparseimage
cd /Volumes/$APP_NAME
ln -s /Applications Applications
cd $WORKDIR
hdiutil detach /Volumes/$APP_NAME

# convert sparseimage to dmg and cleanup 
hdiutil convert ${APP_NAME}.sparseimage -format UDBZ -o ${APP_NAME}.dmg
rm ${APP_NAME}.sparseimage
