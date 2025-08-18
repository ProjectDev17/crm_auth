# crm_auth

#dar permisos a la layer
aws lambda add-layer-version-permission --layer-name common-utils-py312 --version-number 8 --statement-id allow-057326867506 --principal 057326867506 --action lambda:GetLayerVersion --region us-east-1
