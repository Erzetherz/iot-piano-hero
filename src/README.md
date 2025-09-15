# README
cat > iot-piano-hero/README.md << 'EOF'
# Piano-Hero (Raspberry Pi)
Starte mit:
  pip3 install -r requirements.txt
  python3 src/piano_hero.py
Im Browser öffnen: http://<PI-IP>:5000
EOF

# Python-Abhängigkeiten
printf "Flask==3.0.0\nRPi.GPIO==0.7.1\n" > iot-piano-hero/requirements.txt

# .gitignore
printf "__pycache__/\n*.pyc\n.env\nvenv/\n" > iot-piano-hero/.gitignore
