(* ::Package:: *)

BeginPackage["Tskmon`"];


(* ::Section:: *)
(*Usage Strings*)


TskmonClient::usage = "
TskmonClient[token] connects to the tskmon service and allows for creating and updating tasks.
";


FetchTasks::usage = "
FetchTasks[client] fetches a list of current tasks from the tskmon service.
";


TskmonServer::usage = "";


Creator::usage = "";
MaxProgress::usage = "";


NewTask::usage = "";
UpdateTask::usage = "";
DeleteTask::usage = "";


Task::usage = "";


(* ::Section:: *)
(*Private*)


Begin["`Private`"];


(* ::Subsection:: *)
(*Options*)


Options[TskmonClient] = {
	TskmonServer -> "https://tskmon.herokuapp.com"
};


Options[NewTask] = {
	Creator -> "Mathematica",
	MaxProgress -> 100
};


(* ::Subsection:: *)
(*Properties*)


Token[TskmonClient[token_, OptionsPattern[]]] := token;


TskmonServer[TskmonClient[token_, opts : OptionsPattern[]]] := OptionValue[TskmonClient, opts, TskmonServer];


(* ::Subsection:: *)
(*Utility Functions*)


TskmonURL[client_TskmonClient,path_] := StringJoin[TskmonServer[client], "/api", path, ".json"];


TskmonURL[task_Task] := TskmonURL[
	"Client" /. List @@ task,
	"/tasks/" <> ToString["id" /. List @@ task]
];


TskmonHeaders[client_TskmonClient] := {
	"Authorization" -> "Token " <> Token[client],
	"Content-Type" -> "application/json"
}


(* ::Subsection:: *)
(*Formatting*)


Format[client_TskmonClient] := Interpretation[TskmonClient, "TskmonClient"][Interpretation["(token hidden)", Null]];


Format[task_Task] := Interpretation[Task, "Task"][Interpretation[Column[{
	"description" /. List @@ task,
	"status" /. List @@ task,
	ProgressIndicator[
		"current_progress" /. List @@ task,
		{0, "max_progress" /. List @@ task}
	]
}], Null]]


(* ::Subsection:: *)
(*Task Management*)


FetchTasks[client_TskmonClient] := 
	Task[##, "Client"->client]& @@@ ImportString[
		URLFetch[
			TskmonURL[client, "/tasks/"],
			"Headers" -> TskmonHeaders[client]
		], "JSON"
	]


NewTask[
	client_TskmonClient,
	description_,
	status_,
	currentProgress_,
	OptionsPattern[]
] := With[
	{body = ExportString[{
		"description" -> description,
		"status" -> status,
		"current_progress" -> currentProgress,
		"creator" -> OptionValue[Creator],
		"max_progress" -> OptionValue[MaxProgress]
	}, "JSON"]},

	Task@@Join[ImportString[URLFetch[
		"https://tskmon.herokuapp.com/api/tasks/.json",
		"Method"->"POST",
		"Headers"->TskmonHeaders[client],
		"BodyData"->body
	],"JSON"], {"Client"->client}]
];


UpdateTask[task_Task, params__Rule] := With[
	{body = ExportString[{
		params
	}, "JSON"]},

	Module[{resp},
		resp = URLFetch[
			TskmonURL[task],
			"Method" -> "PUT",
			"Headers" -> TskmonHeaders["Client" /. List @@ task],
			"BodyData" -> body
		];
		Task @@ Join[ImportString[resp, "JSON"], {"Client" -> client}]
	]
];


DeleteTask[task_Task] := URLFetch[
	TskmonURL[task],
	"Method" -> "DELETE",
	"Headers" -> TskmonHeaders["Client" /. List @@ task]
];


End[];


EndPackage[];
