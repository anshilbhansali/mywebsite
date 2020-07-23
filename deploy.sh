#!/bin/bash
echo 
echo "********************************************************************"
echo "Starting to build docker image"
echo "********************************************************************"
echo " "
docker build -t anshils-website .
echo "********************************************************************"
echo "Docker image built, now tagging it"
echo "********************************************************************"
echo " "
docker tag anshils-website 848744644080.dkr.ecr.us-east-2.amazonaws.com/anshils-website
echo "********************************************************************"
echo "Tagging done, now pushing to ECR"
echo "********************************************************************"
echo " "
$(aws ecr get-login --no-include-email --region us-east-2)
docker push 848744644080.dkr.ecr.us-east-2.amazonaws.com/anshils-website
echo "********************************************************************"
echo "Pushed to ECR"
echo "********************************************************************"
echo " "

echo "********************************************************************"
echo "Now forcing new deployment for ecs service"
echo "********************************************************************"
echo " "
aws ecs update-service --cluster anshils-website-cluster --service anshils-website-container-service --force-new-deployment
echo "Done"
