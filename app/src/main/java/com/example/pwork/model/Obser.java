package com.example.pwork.model;

import androidx.room.Entity;
import androidx.room.PrimaryKey;

@Entity(tableName = "observations")
public class Obser {
    @PrimaryKey(autoGenerate = true)
    public int id;
    public String observation;
    public String timeOfObservation;
    public String comments;
}

