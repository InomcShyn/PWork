package com.example.pwork.view.editview;

import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import com.example.pwork.R;
import com.example.pwork.database.HikeDatabase;
import com.example.pwork.model.Obser;

public class EditOb extends AppCompatActivity {

    private EditText observationEditText, timeOfObservationEditText, commentsEditText;
    private Button editObservationButton;
    private ImageButton customButton;
    private HikeDatabase db;
    private Obser observation;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_edit_ob);

        db = HikeDatabase.getDatabase(getApplicationContext());

        observationEditText = findViewById(R.id.observationEditText);
        timeOfObservationEditText = findViewById(R.id.timeOfObservationEditText);
        commentsEditText = findViewById(R.id.commentsEditText);
        editObservationButton = findViewById(R.id.addObservationButton);

        // Retrieve the observation data passed from the previous activity
        int observationId = getIntent().getIntExtra("observation_id", -1); // Mặc định -1 nếu không tìm thấy
        String observationText = getIntent().getStringExtra("observation_observation");
        String timeOfObservationText = getIntent().getStringExtra("observation_time");
        String commentsText = getIntent().getStringExtra("observation_comments");

        observation = new Obser();
        observation.id = observationId;
        observation.observation = observationText;
        observation.timeOfObservation = timeOfObservationText;
        observation.comments = commentsText;

        customButton = findViewById(R.id.custom_button);
        customButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                finish();
            }
        });

        if (observation != null) {
            // Populate the EditText fields with the existing observation data
            observationEditText.setText(observation.observation);
            timeOfObservationEditText.setText(observation.timeOfObservation);
            commentsEditText.setText(observation.comments);
        }

        editObservationButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String updatedObservation = observationEditText.getText().toString().trim();
                String updatedTimeOfObservation = timeOfObservationEditText.getText().toString().trim();
                String updatedComments = commentsEditText.getText().toString().trim();

                if (!validateInput(updatedObservation, updatedTimeOfObservation)) {
                    Toast.makeText(EditOb.this, "Invalid input provided", Toast.LENGTH_SHORT).show();
                    return;
                }

                observation.observation = updatedObservation;
                observation.timeOfObservation = updatedTimeOfObservation;
                observation.comments = updatedComments;

                new Thread(new Runnable() {
                    @Override
                    public void run() {
                        db.observationDao().update(observation);
                        runOnUiThread(new Runnable() {
                            @Override
                            public void run() {
                                Toast.makeText(getApplicationContext(), "Observation successfully updated", Toast.LENGTH_SHORT).show();
                                finish();
                            }
                        });
                    }
                }).start();
            }
        });
    }

    private boolean validateInput(String observation, String timeOfObservation) {
        return !observation.isEmpty() && !timeOfObservation.isEmpty();
    }
}
