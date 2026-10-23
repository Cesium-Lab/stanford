using Base.Iterators: product


###############################################################################################
#           Definitions
###############################################################################################

# Variable struct with possible values
struct Variable
    name::Symbol # not exactly sure what this is
    r::Int # values
end

# e.g. (x=1, y=1, z=2)
const Assignment = Dict{Symbol, Int} # Maps a symbol to its value for a sample

# e.g. { (x=1, y=1, z=2) => 0.5}
const FactorTable = Dict{Assignment, Float64} # Probability of that sample occurring

# thing that has variables, and maps assignments to their probabilities
struct Factor
    vars::Vector{Variable} # inputs? ish
    table::FactorTable
end

""" Gets variable """
vars_names_in(ϕ::Factor) = [var.name for var in ϕ.vars]

"""Maps name to its value"""
select(a::Assignment, varnames::Vector{Symbol}) = 
    Assignment(n=>a[n] for n in varnames)

# AbstractVector: vector base type
# Enumerating assignments (e.g. 0,0,0,0 and 0,0,0,1)
function assignments(vars::AbstractVector{Variable})
    names::Vector{Symbol} = [var.name for var in vars]

    # Vec squashes the array to a vector
    # Product is iterations so like 
    return vec([
        Assignment(n=>v for (n,v) in zip(names, values))
        for values in product((1:v.r for v in vars)...) # THIS UNPACKS (nice)
    ])
end


"""
function assignments(vars::AbstractVector{Variable})
    names::Vector{Symbol} = [var.name for var in vars]
    var_values = [value for value in product((1:v.r for v in vars)...)]

    # Vec squashes the array to a vector
    # Product is iterations so like 
    return vec([
        Assignment(n=>v for (n,v) in zip(names, values))
        for values in var_values # THIS UNPACKS (nice)
    ])
end
"""

""" ϕ: factor table """
function normalize!(ϕ::Factor)
    # Adds all probabilities
    z = sum(probability for (assignment,probability) in ϕ.table) 

    for (assignment,probability) in ϕ.table
        ϕ.table[assignment] = probability/z
    end

end

function normalize(ϕ::Factor)
    # Adds all probabilities
    z = sum(probability for (assignment,probability) in ϕ.table) 
    table = FactorTable()
    for (assignment,probability) in ϕ.table
        table[assignment] = probability/z
    end

    return Factor(ϕ.vars, table)

end



###############################################################################################
#           Convenience
###############################################################################################

Base.Dict{Symbol,V}(a::NamedTuple) where V =
    Dict{Symbol,V}(n=>v for (n,v) in zip(keys(a), values(a)))
Base.convert(::Type{Dict{Symbol,V}}, a::NamedTuple) where V =
    Dict{Symbol,V}(a)
Base.isequal(a::Dict{Symbol,<:Any}, nt::NamedTuple) =
    length(a) == length(nt) &&
    all(a[n] == v for (n,v) in zip(keys(nt), values(nt)))

function print_factor(ϕ::Factor)
    println("Factor with: $(ϕ.vars)")
    for row in ϕ.table
        println(row)
    end
    println()
end

###############################################################################################
#           Code
###############################################################################################