---
title: 'Batch Calculator: a tool for material batch calculations'
tags:
  - Batch composition
  - zeolites
  - synthesis
  - glass
  - ceramics
authors:
 - name: Katarzyna Anna Łukaszuk
   orcid: 0000-0003-0870-9252
   affiliation: 1
 - name: Łukasz Michal Mentel
   orcid: 0000-0001-9986-1262
   affiliation: 2
affiliations:
 - name: "Center for Materials Science and Nanotechnology (SMN), Department of Chemistry, University of Oslo, Oslo, Norway"
   index: 1
 - name: Arundo Analytics AS, Oslo, Norway
   index: 2
date: 23 April 2018
bibliography: paper.bib
---

# Summary

The struggle with reproducibility of experiments is commonly known for many
scientists. Undoubtedly, in the field of material science, this problem can be
a consequence of lack of a well-established methodology in synthesis
procedure. The experience gained during preparation of zeolites - inorganic
aluminosilicates, indicated that there is a room for improvement in how
synthesis of materials requiring batch preparation stage (not only zeolites,
but also glass, ceramics, clay) is done, reported and shared.

The batch preparation involves calculation, weighting out and mixing raw materials
according to a recipe given as the molar ratio of oxide components i.e.
batch composition:

*M$_2$O : Al$_2$O$_3$ : xSiO$_2$ : ySDA : zH$_2$O + q anything else that is added*.

The above form of batch composition notation is applied even if the oxide
themselves are not used as reactants, what very often lead to errors in batch composition calculations.

Batch Calculator is a GUI script based on wxPython, which speeds up the
tendious part of batch preparation by converting the molar composition into
reactant masses (and volumes) and back. It allow to build, edit, reuse and
share a well-structured database of reactants, as well as interactively
explore the batch composition by changing the molar ratios, chemicals used,
concentrations, etc. Moreover, database with essential components and common
chemicals used for zeolite synthesis is already inlcuded. Scaling to a
specific batch size is another feature of this open-source tool. All the
details about synthesis can be easily generate in a form of customizable
report, which can be shared with other researchers .

Batch Calculator aims to increase an experimental rigor, reporting
transparency, and thus reproducibility of experiments. We believe it will
become a standard tool widely accepted by material science community.


-![Fidgit deposited in figshare.](figshare_article.png)

# References
