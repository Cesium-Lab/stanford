using Graphs

include("./helpers.jl")

###############################################################################################
#           Definitions
###############################################################################################

struct BayesianNetwork
    vars::Vector{Variable} # Like the nodes on the graph
    factors::Vector{Factor} # the actual factor for those variables
    graph::SimpleDiGraph{Int64} # Has the edges between specific IDs
end

""" Function finding name=>value of assignment in a factor """
function probability(bn::BayesianNetwork, assignment::Assignment)
    # For a factor, finds what each variable in the factor's value is
    # e.g. for [X, Y, Z] finds what :x, :y, and :z are in the assignment
    subassignment(ϕ) = select(assignment, variablenames(ϕ))

    # Function finding probability of that subassignment being in the table
    probability(ϕ) = get(ϕ.table, subassignment(ϕ), 0.0)

    return prod(probability(ϕ) for ϕ in bn.factors)
end

# TODO: Algorithm 2.3

###############################################################################################
#           Code
###############################################################################################

if abspath(PROGRAM_FILE) == @__FILE__
    B = Variable(:b, 2); S = Variable(:s, 2); # Upper layer
    E = Variable(:e, 2); # Middle layer
    D = Variable(:d, 2); C = Variable(:c, 2); # Lower layer
    vars = [B, S, E, D, C]

    factors = [
        # Node B depends only on B
        Factor([B], FactorTable( 
            (b=1,) => 0.99, (b=2,) => 0.01)),
        # Node S depends only on S
        Factor([S], FactorTable(
            (s=1,) => 0.98, (s=2,) => 0.02)),
        # Node E depends on E< but also its parents B and S
        Factor([E, B, S], FactorTable(
            (e=1,b=1,s=1) => 0.90, (e=1,b=1,s=2) => 0.04,
            (e=1,b=2,s=1) => 0.05, (e=1,b=2,s=2) => 0.01,
            (e=2,b=1,s=1) => 0.10, (e=2,b=1,s=2) => 0.96,
            (e=2,b=2,s=1) => 0.95, (e=2,b=2,s=2) => 0.99)),
        # Node D depends on D and parent E
        Factor([D, E], FactorTable(
            (d=1,e=1) => 0.96, (d=1,e=2) => 0.03,
            (d=2,e=1) => 0.04, (d=2,e=2) => 0.97)),
        # Node C depends on C and parent E
            Factor([C, E], FactorTable(
            (c=1,e=1) => 0.98, (c=1,e=2) => 0.01,
            (c=2,e=1) => 0.02, (c=2,e=2) => 0.99))
    ]
    graph = SimpleDiGraph(5)
    add_edge!(graph, 1, 3); add_edge!(graph, 2, 3)
    add_edge!(graph, 3, 4); add_edge!(graph, 3, 5)

    bn = BayesianNetwork(vars, factors, graph)
    println(bn)

    assignment = Assignment(b=0, s=0, e=0, d=0, c=0)
    println(assignment)
    p = probability(bn, assignment)
    println(p)
end

