# Tecnical details of QUATIS

QUATIS runs on the edX platform, which is an open learning platform to create and your own courses. edX is being used by many universities, so it's pretty known.

QUATIS can be added as an exercise on a edX course. Then it can be congfigured like the title, graph, etc.

Here we are going to show thew technical details on this

QUATIS was developed using XBlocks, which are used to create the exercises for the Open edX platform

XBlocks utilizes Phython in the backend, while using HTML, CSS and javascript for the front-end.

# Front-end
The front-end ewas developed using HTTP, CSS and Javascript. No UI editor was used to create the interface.

# Back-end
Every XBlock is developed using Phython

# Details
As mentioned on the README, the main steps of a common uso of QUATIS would be the following:
1. The teacher adds the exercise, and customize both the data (like title and descrption) and the knowledge graph
2. Students will start doing the exercise
3. Student's data, like new solutions and feedbacks, are added to the graph
4. From time to time, the teacher will check the graph and correct it

We will now include more specific details on how each step occurs in the backend part of it

## Step 1
The information from the exercise, like the title, description, alternatives, etc are all set using the XBlock fields, which you can customize to be the same value for everyone or be unique for each student. You can see more information about it [here](https://edx.readthedocs.io/projects/xblock-tutorial/en/latest/concepts/fields.html)

The graph's elements like the nodes and edges were initially represented using Dicts (which can also be XBlocks variables), which are also known as maps in other languages like Java. 
Because of limitations of the XBlock, which is that it's variables cannot bew modified by both teachers and students, it was migrated to the MySQL DB, which every elemento of the graph is included there.

The tables are separated for on of each element from the graph. These are the main ones:

- Problem (Base element, includes the Id of the problem, which is also an XBlock variable, and it's used to bridge the XBlock variables and the MySQL DB)
- Node
- Edge
- Resolution (represent a solution that the student made during the exercise. Each student that used QUATIS will have an entry here)
- Attempt (every time a stunde tries an exercise, it will add an attempt in this table)
- Hint
- Explanation
- Error Specific Feedbacks
- Doubts
- Answers

Each table above also inclujdes a history table, which stores the changes made to every element of the graph

Also, for safety purposes, QUATIS will also do a backup of all tables every hour. It can be used to rollback or recover the information in case of emergency, or for studies

## Step 2
During the exercise, every time a student loads the page, QUATIS will count both the time it started and also an attempt


## Step 3

When sending the answer, QUATIS will use the step-by-step solution and the selected option and analyze both.
If all nodes and edges from the Step-by-step solution are coorect/vald, and the selected option is also the correct one, it will share the message that the solution is correct.
If at least one node is incorrect or one edge is invalid, it will show the response message that the solution is incorrect
If some element still have the correctness or the validy as unknown, the response message will say that the solution is still in analysis.

After checking if the solution is correct, QUATIS will check on the graph which nodes and edges still need to be checked if they are correct, and also which edges may bstill need feedbacks to be added, for example when a student adds new nodes and edges, they won't have any feedbacks like hints. These informations can also be added by students.

When finishing the exercise and sending all asked feedbacks, the timer will stop, thus completing the information about the student's solution (available on the **resolution** table)



# Backend calls
During the usage of QUATIS for both teachers and students, you may need to communicate with the QUATIS back end system in roder to obtain or update data. Here is the list of calls that you can do. This may be useful if you want to explore the system further:

## For students

- finish_activity_time: each solution that a student uses also incluides a timer when it started and finished for analysis if needed. This call will set the finish time of it. It's called right after the student sends all asked feedback from QUATIS
- update_resolution_correctness: QUATIS keeps an saved solution and also calculates it's correctness based on the correctness of the nodes and validity of the edges
- increase_feedback_count: increase the amount of times a feedback was seem
- send_answer: send the student's solution to QUATIS, for checking if it'1s correct
- send_feedback: creates the feedback that the student sents
- recommend_feedback: it increase or decrease the usefulness of a feedback
- get_doubts_and_answers_from_step: obtain the doubts and answers from other students on a certain step (graph's edge)
- get_doubts_and_answers_from_state: obtain the doubts and answers from other students on a certain state (graph's node)
- update_positions: the generate graph will try to position the new edges and nodes to increase visibility of the graph's elements
- get_hint_for_last_step: analyzes the current solution of the student, and sends the most proper feedback

## For teachers

- initial_data: when QUATIS is initially added as a component, a simple graph is generated here as a example
- generate_problem_id: initial call to generate the problem ID, which will be used to uniquely identify the exercise
- submit_data: update the exercise's data (like title and description). It does not include the knoiwledge graph
- generate_graph: generate the visual representation of the graph
- get_edge_info: obtain the information from the selected edge
- import_data: import a exercise data and graph in JSON format to the current QUATIS component
- reset_counters: resets every edge, node and feedback counter to 0
- delete_doubts: delete the specific doubt
- delete_answers: delete the specific answer
- delete_feedbacks: delete the specific hint, explanation or error specific
- submit_node_info: updates the selected node data 
- submit_edge_info: updates the selected edge data 
- export_data: obtain the data of the exercise and its graph as a JSON format for later import
- submit_graph_data: updates the knowledge graph
- submit_doubt_answer_info: updates the doubt and/or the answer data
- generate_report: generate an experimental report which includes information that could be useful for teachers, like most used edges by students

