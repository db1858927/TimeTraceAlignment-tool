# TimeTraceAlignment Tool

## Overview
TimeTraceAligner, takes as input a process log, specified in the XES(eXtensibleEventStream)format,
and a set of MTL or LTL formulas expressed using the time-constrained Declare language. (.decl file).
The tool outputs the problem in PDDL, which can be directly executed using the ENHSP planner.

## Prerequisites
Before using the TimeTraceAlignment tool, ensure you have the following installed:

1. **Python 3.x** 
Make sure Python 3.x is installed on your machine.

3. **ENSHP Package**
Download and install the ENSHP20 package from [ENSHP Official Website]([https://sites.google.com/view/enhsp/]).
Follow the installation instructions provided on the website.

## Installation and Launch

The TimeTraceAligner tool is executed via the command line, providing several options to
customize the input and control how the alignment is performed. 
The script is invoked using the following options:

- log : Specifies the path to the XES log file containing the process traces. This file
is essential as it contains the sequences of activities that will be aligned. The file must
conform to the XES (eXtensible Event Stream) standard.
- decl : Defines the path to the DECL (Declare) file that contains the temporal con-
straints and rules, expressed using Metric Temporal Logic (MTL) formulas. These con-
straints are critical in determining the time-based conditions for aligning the activities
in the log file.
-dom : Specifies the domain type, which governs how the temporal constraints are
applied and which variant of the planning problem is generated. The available domain
types are:
  * LTL-d: Linear Temporal Logic with duration.
  * MTL: Metric Temporal Logic, which supports time-bounded constraints.
  * MTL-d: Metric Temporal Logic with duration.

```bash
Example Usage:
python main.py -log example_log.xes -decl example_constraints.decl -dom MTL
