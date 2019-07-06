|#|Server|Client|Jump|
|:-|:-:|:-:|:-|
|1|INIT $NUMBER_OF_CHUNKS|||
|2||ACK||
|3|DATA $CHUNK_DATA|||
|4||ACK|GOTO #3 FOR $NUMBER_OF_CHUNKS TIMES|
|5|DONE|||
