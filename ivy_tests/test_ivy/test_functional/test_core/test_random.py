"""Collection of tests for unified reduction functions."""

# global
import numpy as np
from hypothesis import given, assume, strategies as st

# local
import ivy
import ivy.functional.backends.numpy as ivy_np
import ivy_tests.test_ivy.helpers as helpers
from ivy_tests.test_ivy.helpers import handle_cmd_line_args


# random_uniform
@handle_cmd_line_args
@given(
    dtype_and_low=helpers.dtype_and_values(
        available_dtypes=helpers.get_dtypes("float"),
        min_value=-1000,
        max_value=100,
        min_num_dims=1,
        max_num_dims=5,
        min_dim_size=2,
    ),
    dtype_and_high=helpers.dtype_and_values(
        available_dtypes=helpers.get_dtypes("float"),
        min_value=101,
        max_value=1000,
        min_num_dims=1,
        max_num_dims=5,
        min_dim_size=2,
    ),
    dtype=helpers.get_dtypes("float", full=False),
    num_positional_args=helpers.num_positional_args(fn_name="random_uniform"),
)
def test_random_uniform(
    dtype_and_low,
    dtype_and_high,
    dtype,
    as_variable,
    with_out,
    num_positional_args,
    native_array,
    container,
    instance_method,
    fw,
    device,
):
    low_dtype, low = dtype_and_low
    high_dtype, high = dtype_and_high
    ret, ret_gt = helpers.test_function(
        input_dtypes=[low_dtype, high_dtype],
        as_variable_flags=as_variable,
        with_out=with_out,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        container_flags=container,
        instance_method=instance_method,
        test_values=False,
        fw=fw,
        fn_name="random_uniform",
        low=np.asarray(low, dtype=low_dtype),
        high=np.asarray(high, dtype=high_dtype),
        shape=None,
        dtype=dtype,
        device=device,
    )
    ret = helpers.flatten_and_to_np(ret=ret)
    ret_gt = helpers.flatten_and_to_np(ret=ret_gt)
    for (u, v) in zip(ret, ret_gt):
        assert u.dtype == v.dtype


# random_normal
@handle_cmd_line_args
@given(
    dtype_and_mean=helpers.dtype_and_values(
        available_dtypes=helpers.get_dtypes("float"),
        min_value=-1000,
        max_value=1000,
        min_num_dims=1,
        max_num_dims=5,
        min_dim_size=2,
    ),
    dtype_and_std=helpers.dtype_and_values(
        available_dtypes=helpers.get_dtypes("float"),
        min_value=0,
        max_value=1000,
        min_num_dims=1,
        max_num_dims=5,
        min_dim_size=2,
    ),
    dtype=helpers.get_dtypes("float", full=False),
    num_positional_args=helpers.num_positional_args(fn_name="random_normal"),
)
def test_random_normal(
    dtype_and_mean,
    dtype_and_std,
    dtype,
    as_variable,
    with_out,
    num_positional_args,
    native_array,
    container,
    instance_method,
    fw,
    device,
):
    mean_dtype, mean = dtype_and_mean
    std_dtype, std = dtype_and_std
    ret, ret_gt = helpers.test_function(
        input_dtypes=[mean_dtype, std_dtype],
        as_variable_flags=as_variable,
        with_out=with_out,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        container_flags=container,
        instance_method=instance_method,
        test_values=False,
        fw=fw,
        fn_name="random_normal",
        mean=np.asarray(mean, dtype=mean_dtype),
        std=np.asarray(std, dtype=std_dtype),
        shape=None,
        dtype=dtype,
        device=device,
    )
    ret = helpers.flatten_and_to_np(ret=ret)
    ret_gt = helpers.flatten_and_to_np(ret=ret_gt)
    for (u, v) in zip(ret, ret_gt):
        assert u.dtype == v.dtype


@st.composite
def _pop_size_num_samples_replace_n_probs(draw):
    prob_dtype = draw(helpers.get_dtypes("float", full=False))
    batch_size = draw(helpers.ints(min_value=1, max_value=5))
    population_size = draw(helpers.ints(min_value=1, max_value=20))
    replace = draw(st.booleans())
    if replace:
        num_samples = draw(helpers.ints(min_value=1, max_value=20))
    else:
        num_samples = draw(helpers.ints(min_value=1, max_value=population_size))
    probs = draw(
        helpers.array_values(
            dtype=prob_dtype,
            shape=[batch_size, num_samples],
            min_value=1.0013580322265625e-05,
            max_value=1.0,
            exclude_min=True,
            large_value_safety_factor=1.25,
        )
    )
    return prob_dtype, batch_size, population_size, num_samples, replace, probs


# multinomial
@handle_cmd_line_args
@given(
    everything=_pop_size_num_samples_replace_n_probs(),
)
def test_multinomial(
    everything,
    as_variable,
    with_out,
    native_array,
    container,
    instance_method,
    fw,
    device,
):
    prob_dtype, batch_size, population_size, num_samples, replace, probs = everything
    # tensorflow does not support multinomial without replacement
    assume(not (fw == "tensorflow" and not replace))
    ret = helpers.test_function(
        input_dtypes=[prob_dtype],
        as_variable_flags=as_variable,
        with_out=with_out,
        num_positional_args=2,
        native_array_flags=native_array,
        container_flags=container,
        instance_method=instance_method,
        fw=fw,
        fn_name="multinomial",
        test_values=False,
        ground_truth_backend="numpy",
        population_size=population_size,
        num_samples=num_samples,
        batch_size=batch_size,
        probs=np.asarray(probs, dtype=prob_dtype) if probs is not None else probs,
        replace=replace,
        device=device,
    )
    if not ivy.exists(ret):
        return
    ret_np, ret_from_np = ret
    ret_np = helpers.flatten_and_to_np(ret=ret_np)
    ret_from_np = helpers.flatten_and_to_np(ret=ret_from_np)
    for (u, v) in zip(ret_np, ret_from_np):
        assert u.dtype == v.dtype


# randint
@handle_cmd_line_args
@given(
    dtype_and_low=helpers.dtype_and_values(
        available_dtypes=tuple(
            set(ivy_np.valid_int_dtypes).difference(set(ivy_np.valid_uint_dtypes))
        ),
        min_value=-100,
        max_value=25,
    ),
    dtype_and_high=helpers.dtype_and_values(
        available_dtypes=tuple(
            set(ivy_np.valid_int_dtypes).difference(set(ivy_np.valid_uint_dtypes))
        ),
        min_value=26,
        max_value=100,
    ),
    dtype=st.sampled_from(("int8", "int16", "int32", "int64")),
    num_positional_args=helpers.num_positional_args(fn_name="randint"),
)
def test_randint(
    dtype_and_low,
    dtype_and_high,
    dtype,
    as_variable,
    with_out,
    num_positional_args,
    native_array,
    container,
    instance_method,
    fw,
    device,
):
    low_dtype, low = dtype_and_low
    high_dtype, high = dtype_and_high
    ret, ret_gt = helpers.test_function(
        input_dtypes=[low_dtype, high_dtype],
        as_variable_flags=as_variable,
        with_out=with_out,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        container_flags=container,
        instance_method=instance_method,
        test_values=False,
        fw=fw,
        fn_name="randint",
        low=np.asarray(low, dtype=low_dtype),
        high=np.asarray(high, dtype=high_dtype),
        shape=None,
        dtype=dtype,
        device=device,
    )
    ret = helpers.flatten_and_to_np(ret=ret)
    ret_gt = helpers.flatten_and_to_np(ret=ret_gt)
    for (u, v) in zip(ret, ret_gt):
        assert ivy.all(u >= low) and ivy.all(u < high)
        assert ivy.all(v >= low) and ivy.all(v < high)


# seed
@handle_cmd_line_args
@given(
    seed_val=helpers.ints(min_value=0, max_value=2147483647),
)
def test_seed(seed_val):
    # smoke test
    ivy.seed(seed_value=seed_val)


# shuffle
@handle_cmd_line_args
@given(
    dtype_and_x=helpers.dtype_and_values(
        available_dtypes=helpers.get_dtypes("float"),
        allow_inf=False,
        min_num_dims=1,
        min_dim_size=2,
    ),
    num_positional_args=helpers.num_positional_args(fn_name="shuffle"),
)
def test_shuffle(
    dtype_and_x,
    as_variable,
    with_out,
    num_positional_args,
    native_array,
    container,
    instance_method,
    fw,
):
    dtype, x = dtype_and_x
    ret, ret_gt = helpers.test_function(
        input_dtypes=[dtype],
        as_variable_flags=as_variable,
        with_out=with_out,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        container_flags=container,
        instance_method=instance_method,
        test_values=False,
        fw=fw,
        fn_name="shuffle",
        x=np.asarray(x, dtype=dtype),
    )
    ret = helpers.flatten_and_to_np(ret=ret)
    ret_gt = helpers.flatten_and_to_np(ret=ret_gt)
    for (u, v) in zip(ret, ret_gt):
        assert ivy.all(ivy.sort(u, axis=0) == ivy.sort(v, axis=0))
