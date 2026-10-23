
include("./helpers.jl")
include("./bayesian_networks.jl")

###############################################################################################
#           Definitions
###############################################################################################

#####################################
#           Factor Product
#####################################

# Factor product
function Base.:*(factor1::Factor, factor2::Factor)
    vars = vcat(factor1.vars, factor2.vars) # For constructor
    
    table = FactorTable() # For constructor

    names_1 = vars_names_in(factor1)
    names_2 = vars_names_in(factor2)

    names_1_only = setdiff(names_1.vars, name_2.vars)
    for (assignments_1, prob_1) in names_1.table
        for a in assignments(names_1_only)
            a = merge(assignments_1, a)
            assignments_2 = select(a, names_2)
            table[a] = prob_1 * get(
                factor2.table, assignments_2, 0.0)
        end
    end
    
    return Factor(vars, table)
end

#####################################
#           Marginalize
#####################################

function marginalize(ϕ::Factor, name::Symbol)
    table = FactorTable()
    for (assignments, prob) in ϕ.table
        # For each assignment "row", get row without "name" variable
        # e.g. (x=1, y=1, z=1) -> (x=1, z=1)
        a_1 = delete!(copy(assignments), name)

        # Add that probability to the row without the name
        # e.g. if (x=1, y=1, z=1) = 0.08
        #   then it would be (x=1, z=1) += 0.08
        table[a_1] = get(table, a_1, 0.0) + prob
    end

    vars = filter(v -> v.name != name, ϕ.vars)
    return Factor(vars, table)

end

#####################################
#           Condition
#####################################

# # Is the variable name in the factor
in_scope(name, ϕ) = any(name == v.name for v in ϕ.vars)

function condition(ϕ::Factor, name::Symbol, value::Int)
    # Checks if variable is actually in the factor
    if !in_scope(name, ϕ)
        return ϕ
    end
    
    table = FactorTable()
    for (assignment, prob) in ϕ.table
        if assignment[name] == value
            # Consistent assignment with evidence
            # But removes variable
            # e.g. for y=1, (x=1, y=1, z=1) => 0.2
            #                    -> (x=1, z=1) => 0.2
            table[delete!(copy(assignment), name)] = prob
        end
    end
    vars = filter(v -> v.name != name, ϕ.vars)
    # Returns factor with new table consistent with evidence
    return Factor(vars, table)
end

# Takes in like (x=1, y=1)
function condition(ϕ::Factor, evidence::NamedTuple)
    for (name, value) in pairs(evidence)
        ϕ = condition(ϕ, name, value)
    end
    return ϕ
end

#####################################
#           Exact Inference
#####################################

# TODO: Algorithm 3.4
struct ExactInference end # Used for Multiple Dispatch

# Compute product of all factors, condition based on evidence,
# marginalize hidden variables, and normalize
function infer(M::ExactInference, bn::BayesianNetwork, query, evidence)
end

# TODO: Algorithm 3.5
# TODO: Algorithm 3.6
# TODO: Algorithm 3.7
# TODO: Algorithm 3.8


###############################################################################################
#           Code
###############################################################################################


if abspath(PROGRAM_FILE) == @__FILE__

    # Testing Marginalize
    X = Variable(:x, 2) # Can take 2 values
    Y = Variable(:y, 2) # Can take 2 values
    Z = Variable(:z, 2) # Can take 2 values
    vars = [X, Y, Z]

    table = FactorTable(
        (x=0, y=0, z=0) => 0.08,
        (x=0, y=0, z=1) => 0.31,
        (x=0, y=1, z=0) => 0.09,
        (x=0, y=1, z=1) => 0.37,
        (x=1, y=0, z=0) => 0.01,
        (x=1, y=0, z=1) => 0.05,
        (x=1, y=1, z=0) => 0.02,
        (x=1, y=1, z=1) => 0.07,
    )

    # Marginalize
    ϕ = Factor(vars, table)
    print_factor(ϕ)

    new_ϕ = marginalize(ϕ, :y)
    print_factor(new_ϕ)

    # Condition
    conditioned_ϕ = condition(ϕ, :y, 1)
    print_factor(conditioned_ϕ)

    conditioned_ϕ_2 = condition(ϕ, (y=1, x=0))
    print_factor(conditioned_ϕ_2)
    print_factor(normalize(conditioned_ϕ_2))
    print_factor(conditioned_ϕ_2)



end