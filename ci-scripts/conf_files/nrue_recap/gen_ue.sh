for i in $(seq 28 64); do
    sed "s/001010000000028/$(printf '%015d' $i)/g" \
        ./nrue28.uicc.yaml \
        > ./nrue${i}.uicc.yaml
done