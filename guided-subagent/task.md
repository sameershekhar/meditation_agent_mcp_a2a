 Task - 
 
 a task is a stateful, structured unit of work created by a client agent to collaborate with a remote server agent to achieve a specific goal

 Core Characteristics of a Task
• Stateful tracking: Unlike simple text messages, a task maintains its own unique ID, history, and status across multiple interactions.
• Client-created: Tasks are always initiated by the client requesting the action, while the remote server agent maintains and updates the execution state.
• Output generation: The primary objective of a task is to produce a concrete result or artifact (such as a booked flight, a generated report, or a file).


Task Lifecycle States
A task moves through clearly defined states as the remote agent processes the request:
• submitted: The task has been received by the remote agent.
• working: The remote agent is actively processing the work.
• input-required: The agent needs more information or clarification from the client to proceed.
• completed: The task finished successfully and delivered the expected output.
• canceled / failed / rejected: The task was stopped, encountered an error, or was turned down by the server.