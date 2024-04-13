#!/bin/bash

git pull wasp main --ff-only && srcomp deploy . && git push && ssh wasp 'cd compstate && git pull --ff-only' && git fetch wasp
