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

# Graph
The graph was initially represented using Dicts, which are also known as maps in other languages like Java. Because of limitations of the XBlock, it was migrated to the MySQL DB, which every elemento of the graph is included there.

The information from the exercise, like the title, description, alternatives, etc are all set using the XBlock fields, which you can customize to be the same value for everyone or be unique for each student. You can see more information about it [here](https://edx.readthedocs.io/projects/xblock-tutorial/en/latest/concepts/fields.html)

# Backend calls
During the usage of QUATIS for both teachers and students, you may need to communicate with the QUATIS back end system in roder to obtain or update data. Here is the list of calls that you can do. This may be useful if you want to explore the system further:

## For students

- finish_activity_time: each solution that a student uses also incluides a timer when it started and finished for analysis if needed. This call will set the finish time of it. It's called right after the student sends all asked feedback from QUATIS
- update_resolution_correctness: QUATIS keeps an saved solution and also calculates it's correctness based on the correctness of the nodes and validity of the edges
- increase_feedback_count: increase the amount of times a feedback was seem
- send_answer: send the student's solution to QUATIS, for checking if it'1s correct
- send_feedback: creates the feedback that the student sents
- recommend_feedback: it increase or decrease the usefullness of a feedback
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

