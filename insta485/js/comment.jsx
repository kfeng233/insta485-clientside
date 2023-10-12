import React from "react";
import PropTypes from "prop-types";

export default function Comment({
  handleCommentSubmit,
  handleTextChange,
  handleDeleteButton,
  commentText,
  comments,
  postid,
}) {
  /* Display and update comments */
  return (
    <div>
      {comments &&
        comments.map((comment) => (
          <div key={comment.commentid}>
            <a href={comment.ownerShowUrl}>{comment.owner}: </a>
            <span data-testid="comment-text">{comment.text}</span>
            {comment.lognameOwnsThis ? (
              <button
                data-testid="delete-comment-button"
                onClick={() => handleDeleteButton(comment.commentid)}
                type="button"
              >
                Delete comment
              </button>
            ) : null}
          </div>
        ))}
      <div>
        {postid && (
          <form data-testid="comment-form" onSubmit={handleCommentSubmit}>
            <input
              type="text"
              value={commentText}
              onChange={handleTextChange}
            />
          </form>
        )}
      </div>
    </div>
  );
}

Comment.propTypes = {
  handleCommentSubmit: PropTypes.func,
  handleDeleteButton: PropTypes.func,
  handleTextChange: PropTypes.func,
  commentText: PropTypes.string,
  comments: PropTypes.instanceOf(Array),
  postid: PropTypes.number.isRequired,
};

Comment.defaultProps = {
  handleCommentSubmit: () => {
    console.log("Default submit action");
  },
  handleDeleteButton: () => {
    console.log("Dafault delete action");
  },
  handleTextChange: () => {
    console.log("Default text action");
  },
  commentText: "",
  comments: [],
};
