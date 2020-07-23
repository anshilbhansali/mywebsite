#!/bin/bash
echo 
echo "********************************************************************"
echo "Starting to build docker image"
docker build -t anshils-website .
echo "Docker image built, now tagging it"
docker tag anshils-website 848744644080.dkr.ecr.us-east-2.amazonaws.com/anshils-website
ehco "Tagging done, now pushing to ECR"
$(aws ecr get-login --no-include-email --region us-east-2)
docker push 848744644080.dkr.ecr.us-east-2.amazonaws.com/anshils-website
echo "Done!"
