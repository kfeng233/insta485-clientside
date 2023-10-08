import React from "react";
import PropTypes from "prop-types";

export default function Like({
  handleClick,
  numlike,
  likestatus,
  likeurl,
  postid,
  setLikeUrl,
  setLikeStatus,
  setNumLike,
}) {
  console.log(numlike, likestatus);
  return (
    <div>
      <p>
        {numlike} {numlike === 0 || numlike > 1 ? "likes" : "like"}
      </p>
      <p>
        {postid && (
          <button
            type="button"
            onClick={() =>
              handleClick(
                numlike,
                likestatus,
                likeurl,
                postid,
                setLikeUrl,
                setLikeStatus,
                setNumLike,
              )
            }
            data-testid="like-unlike-button"
          >
            {likestatus ? "un" : ""}like
          </button>
        )}
      </p>
    </div>
  );
}

Like.propTypes = {
  handleClick: PropTypes.func.isRequired,
  numlike: PropTypes.number.isRequired,
  likestatus: PropTypes.bool.isRequired,
  likeurl: PropTypes.string.isRequired,
  postid: PropTypes.number.isRequired,
  setLikeUrl: PropTypes.func.isRequired,
  setNumLike: PropTypes.func.isRequired,
  setLikeStatus: PropTypes.func.isRequired,
};
