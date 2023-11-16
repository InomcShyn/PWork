package com.example.pwork.view.editview;

import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import com.example.pwork.R;
import com.example.pwork.database.HikeDatabase;
import com.example.pwork.model.Obser;

public class EditOb extends AppCompatActivity {

    private EditText observationEditText, timeOfObservationEditText, commentsEditText;
    private Button editObservationButton;
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
        observation = getIntent().getParcelableExtra("observation");

        if (observation != null) {
            // Populate the EditText fields with the existing observation data
            observationEditText.setText(observation.observation);
            timeOfObservationEditText.setText(observation.timeOfObservation);
            commentsEditText.setText(observation.comments);
        }

        editObservationButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // Get the updated observation details
                String updatedObservation = observationEditText.getText().toString().trim();
                String updatedTimeOfObservation = timeOfObservationEditText.getText().toString().trim();
                String updatedComments = commentsEditText.getText().toString().trim();

                // Validate input
                if (!validateInput(updatedObservation, updatedTimeOfObservation)) {
                    Toast.makeText(EditOb.this, "Invalid input provided", Toast.LENGTH_SHORT).show();
                    return;
                }

                // Update the observation and save it to the database
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
                                finish(); // Close the activity after updating the observation
                            }
                        });
                    }
                }).start();
            }
        });
    }

    private boolean validateInput(String observation, String timeOfObservation) {
        // You can add your input validation logic here
        return !observation.isEmpty() && !timeOfObservation.isEmpty();
    }
}